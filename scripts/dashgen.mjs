#!/usr/bin/env node
// DashScope 通义万相 (wan2.2-t2i-flash) batch text-to-image generator.
// Async API: create task -> poll /tasks/{id} -> download result URL.
// Usage: NODE_USE_ENV_PROXY=1 DASHSCOPE_API_KEY=sk-... node scripts/dashgen.mjs jobs.json
// jobs.json: [{ "prompt": "...", "size": "1280*720", "out": "luxefur/assets/img/hero.png", "negative": "..." }]

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname } from "node:path";

const KEY = process.env.DASHSCOPE_API_KEY;
if (!KEY) { console.error("DASHSCOPE_API_KEY not set"); process.exit(1); }

const CREATE = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis";
const TASKS = "https://dashscope.aliyuncs.com/api/v1/tasks/";
const MODEL = process.env.DASH_MODEL || "wan2.2-t2i-flash";
const CONCURRENCY = Number(process.env.DASH_CONCURRENCY || 4);
const NEG_DEFAULT = "text, words, letters, watermark, logo, signature, low quality, blurry, deformed, distorted, extra limbs, ugly";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function createTask(job) {
  for (let attempt = 0; attempt < 8; attempt++) {
    const res = await fetch(CREATE, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${KEY}`,
        "X-DashScope-Async": "enable",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: MODEL,
        input: { prompt: job.prompt, negative_prompt: job.negative || NEG_DEFAULT },
        parameters: { size: job.size || "1024*1024", n: 1, prompt_extend: true },
      }),
    });
    const data = await res.json();
    const id = data?.output?.task_id;
    if (id) return id;
    if (data?.code === "Throttling.RateQuota" || res.status === 429) {
      await sleep(5000 + attempt * 3000); // backoff on rate limit
      continue;
    }
    throw new Error("create failed: " + JSON.stringify(data));
  }
  throw new Error("create failed: throttled after retries");
}

async function pollTask(id) {
  for (let i = 0; i < 60; i++) {
    const res = await fetch(TASKS + id, { headers: { Authorization: `Bearer ${KEY}` } });
    const data = await res.json();
    const st = data?.output?.task_status;
    if (st === "SUCCEEDED") {
      const url = data?.output?.results?.[0]?.url;
      if (!url) throw new Error("no url: " + JSON.stringify(data.output));
      return url;
    }
    if (st === "FAILED" || st === "UNKNOWN") throw new Error("task " + st + ": " + (data?.output?.message || ""));
    await sleep(4000);
  }
  throw new Error("poll timeout");
}

async function download(url, out) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("download " + res.status);
  const buf = Buffer.from(await res.arrayBuffer());
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, buf);
  return buf.length;
}

async function runJob(job) {
  try {
    const id = await createTask(job);
    const url = await pollTask(id);
    const bytes = await download(url, job.out);
    console.log(`OK   ${job.out} (${(bytes / 1024).toFixed(0)} KB)`);
    return { out: job.out, ok: true };
  } catch (e) {
    console.log(`FAIL ${job.out} — ${e.message}`);
    return { out: job.out, ok: false, error: e.message };
  }
}

async function main() {
  const jobs = JSON.parse(await readFile(process.argv[2], "utf8"));
  console.log(`${jobs.length} jobs · model ${MODEL} · concurrency ${CONCURRENCY}`);
  const results = [];
  let idx = 0;
  async function worker() {
    while (idx < jobs.length) {
      const j = jobs[idx++];
      results.push(await runJob(j));
    }
  }
  await Promise.all(Array.from({ length: Math.min(CONCURRENCY, jobs.length) }, worker));
  const ok = results.filter((r) => r.ok).length;
  console.log(`\nDONE ${ok}/${jobs.length} succeeded`);
  const failed = results.filter((r) => !r.ok);
  if (failed.length) { console.log("FAILED:"); failed.forEach((f) => console.log("  " + f.out + " :: " + f.error)); process.exitCode = 2; }
}
main();
