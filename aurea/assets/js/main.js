// ===== AUREA — interactions =====
(function () {
  "use strict";

  // Mobile hamburger menu
  var hamburger = document.getElementById("hamburger");
  var nav = document.getElementById("primaryNav");

  if (hamburger && nav) {
    hamburger.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      hamburger.classList.toggle("open", open);
      hamburger.setAttribute("aria-expanded", open ? "true" : "false");
    });

    // Close menu when a nav link is tapped
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("open");
        hamburger.classList.remove("open");
        hamburger.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Chatbot toggle (open/close only — non-functional input)
  var chatToggle = document.getElementById("chatToggle");
  var chatClose = document.getElementById("chatClose");
  var chatPanel = document.getElementById("chatPanel");

  function setChat(open) {
    if (!chatPanel || !chatToggle) return;
    chatPanel.hidden = !open;
    chatToggle.setAttribute("aria-expanded", open ? "true" : "false");
    chatToggle.textContent = open ? "✕" : "💬";
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
})();
