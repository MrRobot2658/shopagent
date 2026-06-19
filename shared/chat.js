/* Shops Agent — shared streaming chat client.
 *
 * Connects the store concierge widgets and the admin Copilot to the FastAPI
 * backend (/api/chat, SSE streaming). Auto-detects which surface it's on from
 * the DOM. Degrades gracefully to a canned message if the backend is offline,
 * so the static Vercel deploy keeps working with no backend.
 */
(function () {
  "use strict";

  var API = (window.SHOPAGENT_API || "") + "/api/chat";

  // Derive the store slug from the URL (/luxefur, /pawmaison, /cupid-sport).
  function storeSlug() {
    var seg = (location.pathname.split("/").filter(Boolean)[0] || "").toLowerCase();
    return ["luxefur", "pawmaison", "cupid-sport"].indexOf(seg) >= 0 ? seg : null;
  }

  // Stream a reply from the backend, calling onDelta(text) for each chunk.
  // Returns a promise resolving to the full text. Rejects if the request fails.
  function streamChat(payload, onDelta) {
    return fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    }).then(function (res) {
      if (!res.ok || !res.body) throw new Error("bad response " + res.status);
      var reader = res.body.getReader();
      var decoder = new TextDecoder();
      var buffer = "";
      var full = "";
      function pump() {
        return reader.read().then(function (r) {
          if (r.done) return full;
          buffer += decoder.decode(r.value, { stream: true });
          var lines = buffer.split("\n");
          buffer = lines.pop();
          lines.forEach(function (line) {
            if (line.indexOf("data:") !== 0) return;
            var data = line.slice(5).trim();
            if (!data || data === "[DONE]") return;
            try {
              var delta = JSON.parse(data).delta || "";
              full += delta;
              onDelta(delta);
            } catch (e) {}
          });
          return pump();
        });
      }
      return pump();
    });
  }

  // Generic widget wiring shared by store + copilot.
  function wire(opts) {
    var input = opts.input,
      sendBtn = opts.sendBtn,
      body = opts.body;
    if (!input || !body) return;
    var history = [];

    function addBubble(text, who) {
      var el = document.createElement("div");
      el.className = opts.bubbleClass + " " + who;
      el.textContent = text;
      body.appendChild(el);
      body.scrollTop = body.scrollHeight;
      return el;
    }

    function send() {
      var text = (input.value || "").trim();
      if (!text) return;
      addBubble(text, opts.userClass);
      history.push({ role: "user", content: text });
      input.value = "";
      var bot = addBubble("", opts.botClass);
      bot.classList.add("is-typing");
      streamChat(
        {
          surface: opts.surface,
          store: opts.store(),
          messages: history.slice(-10),
          stream: true,
        },
        function (delta) {
          bot.classList.remove("is-typing");
          bot.textContent += delta;
          body.scrollTop = body.scrollHeight;
        }
      )
        .then(function (full) {
          bot.classList.remove("is-typing");
          if (full) history.push({ role: "assistant", content: full });
        })
        .catch(function () {
          bot.classList.remove("is-typing");
          bot.textContent = opts.fallback;
        });
    }

    if (sendBtn) sendBtn.addEventListener("click", send);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    // --- Admin Copilot ---
    var cpBody = document.getElementById("copilotBody");
    if (cpBody) {
      var storeSelect = document.getElementById("storeSelect");
      wire({
        input: document.querySelector(".copilot-input input"),
        sendBtn: document.querySelector(".copilot-input button"),
        body: cpBody,
        bubbleClass: "cp-msg",
        userClass: "user",
        botClass: "bot",
        surface: "copilot",
        store: function () {
          return storeSelect ? storeSelect.value : "fur";
        },
        fallback: "（离线）后端未连接。启动 docker compose 后即可获得实时运营回答。",
      });
      return;
    }

    // --- Store concierge ---
    var slug = storeSlug();
    var panel = document.getElementById("chatPanel");
    if (slug && panel) {
      wire({
        input: panel.querySelector(".chat-input input"),
        sendBtn: panel.querySelector(".chat-send"),
        body: panel.querySelector(".chat-body"),
        bubbleClass: "bubble",
        userClass: "user",
        botClass: "bot",
        surface: "store",
        store: function () {
          return slug;
        },
        fallback: "Sorry, our assistant is offline right now. Please try again shortly.",
      });
    }
  });
})();
