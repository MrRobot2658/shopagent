/* PAWMAISON — demo store interactions (vanilla JS) */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    /* ----- Mobile hamburger menu ----- */
    var hamburger = document.getElementById("hamburger");
    var navLeft = document.getElementById("navLeft");

    if (hamburger && navLeft) {
      hamburger.addEventListener("click", function () {
        var isOpen = navLeft.classList.toggle("open");
        hamburger.classList.toggle("open", isOpen);
        hamburger.setAttribute("aria-expanded", isOpen ? "true" : "false");
      });

      // Close the menu when a link is tapped
      navLeft.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
          navLeft.classList.remove("open");
          hamburger.classList.remove("open");
          hamburger.setAttribute("aria-expanded", "false");
        });
      });
    }

    /* ----- Floating AI chatbot toggle ----- */
    var chatToggle = document.getElementById("chatToggle");
    var chatClose = document.getElementById("chatClose");
    var chatPanel = document.getElementById("chatPanel");

    function setChat(open) {
      if (!chatPanel || !chatToggle) return;
      chatPanel.hidden = !open;
      chatToggle.textContent = open ? "✕" : "💬";
      chatToggle.setAttribute("aria-label", open ? "Close chat" : "Open chat");
    }

    if (chatToggle && chatPanel) {
      chatToggle.addEventListener("click", function () {
        setChat(chatPanel.hidden);
      });
    }

    if (chatClose) {
      chatClose.addEventListener("click", function () {
        setChat(false);
      });
    }
  });
})();
