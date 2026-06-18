// ===== CUPID SPORT — interactions =====
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    /* ---- Mobile hamburger menu ---- */
    var hamburger = document.getElementById("hamburger");
    var nav = document.getElementById("navPrimary");

    if (hamburger && nav) {
      hamburger.addEventListener("click", function () {
        var open = nav.classList.toggle("open");
        hamburger.classList.toggle("open", open);
        hamburger.setAttribute("aria-expanded", open ? "true" : "false");
      });

      // Close menu after picking a link
      nav.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
          nav.classList.remove("open");
          hamburger.classList.remove("open");
          hamburger.setAttribute("aria-expanded", "false");
        });
      });
    }

    /* ---- Chatbot widget toggle ---- */
    var chatToggle = document.getElementById("chatToggle");
    var chatClose = document.getElementById("chatClose");
    var chatPanel = document.getElementById("chatPanel");

    function setChat(open) {
      if (!chatPanel || !chatToggle) return;
      chatPanel.classList.toggle("open", open);
      chatPanel.setAttribute("aria-hidden", open ? "false" : "true");
      chatToggle.setAttribute("aria-expanded", open ? "true" : "false");
      chatToggle.textContent = open ? "✕" : "💬";
    }

    if (chatToggle && chatPanel) {
      chatToggle.addEventListener("click", function () {
        setChat(!chatPanel.classList.contains("open"));
      });
    }
    if (chatClose) {
      chatClose.addEventListener("click", function () {
        setChat(false);
      });
    }

    // Close chat on Escape
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setChat(false);
    });
  });
})();
