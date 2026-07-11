// Menu mobile
document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("open");
    });
  }

  // Fermer automatiquement les messages flash après quelques secondes
  document.querySelectorAll(".alert").forEach(function (alertBox) {
    setTimeout(function () {
      alertBox.style.transition = "opacity 0.5s ease";
      alertBox.style.opacity = "0";
      setTimeout(function () { alertBox.remove(); }, 500);
    }, 5000);
  });
});
