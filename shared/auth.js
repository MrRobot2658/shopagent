/* Shops Agent — admin login gate (Redis-backed sessions).
 *
 * On load it checks /api/auth/me. If unauthenticated it shows a login overlay
 * that posts to /api/auth/login (sets an httponly session cookie). If the
 * backend is unreachable it lets you through in "offline demo" mode, so the
 * static Vercel deploy keeps working unchanged.
 */
(function () {
  "use strict";
  var API = window.SHOPAGENT_API || "";

  function overlay() {
    var el = document.createElement("div");
    el.id = "sa-login";
    el.innerHTML =
      '<div class="sa-login-card">' +
      '<h2>Shops Agent 后台登录</h2>' +
      '<p class="sa-login-sub">请使用管理员账号登录</p>' +
      '<form id="sa-login-form">' +
      '<input id="sa-user" type="text" placeholder="用户名" autocomplete="username" value="admin">' +
      '<input id="sa-pass" type="password" placeholder="密码" autocomplete="current-password" value="">' +
      '<button type="submit">登录</button>' +
      '<div class="sa-login-err" id="sa-err"></div>' +
      '<div class="sa-login-hint">演示账号：admin / admin123</div>' +
      "</form></div>";
    var css = document.createElement("style");
    css.textContent =
      "#sa-login{position:fixed;inset:0;z-index:99999;background:rgba(11,17,32,.96);display:flex;align-items:center;justify-content:center}" +
      ".sa-login-card{background:#fff;border-radius:16px;padding:34px 30px;width:340px;max-width:90vw;box-shadow:0 20px 60px rgba(0,0,0,.4);font-family:system-ui,-apple-system,sans-serif}" +
      ".sa-login-card h2{margin:0 0 6px;font-size:20px;color:#0f172a}" +
      ".sa-login-sub{margin:0 0 18px;color:#64748b;font-size:13px}" +
      "#sa-login-form{display:flex;flex-direction:column;gap:12px}" +
      ".sa-login-card input{padding:12px 14px;border:1px solid #e2e8f0;border-radius:10px;font:inherit}" +
      ".sa-login-card button{padding:12px;border:0;border-radius:10px;background:#0f172a;color:#fff;font-weight:600;cursor:pointer}" +
      ".sa-login-card button:hover{background:#1e293b}" +
      ".sa-login-err{color:#dc2626;font-size:13px;min-height:16px}" +
      ".sa-login-hint{color:#94a3b8;font-size:12px;text-align:center}";
    document.head.appendChild(css);
    document.body.appendChild(el);

    document.getElementById("sa-login-form").addEventListener("submit", function (e) {
      e.preventDefault();
      var err = document.getElementById("sa-err");
      err.textContent = "";
      fetch(API + "/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({
          username: document.getElementById("sa-user").value,
          password: document.getElementById("sa-pass").value,
        }),
      })
        .then(function (r) {
          if (r.ok) return r.json();
          return r.json().then(function (j) {
            throw new Error(j.detail || "登录失败");
          });
        })
        .then(function () {
          el.remove();
        })
        .catch(function (e2) {
          err.textContent = e2.message || "登录失败";
        });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    fetch(API + "/api/auth/me", { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) overlay(); // 401 -> show login
      })
      .catch(function () {
        /* backend offline -> offline demo mode, no gate */
      });
  });
})();
