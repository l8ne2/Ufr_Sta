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
  // Lightbox : agrandir une photo de la galerie au clic
  const lightbox = document.getElementById("lightbox-overlay");
  const lightboxImg = document.getElementById("lightbox-image");
  const lightboxClose = document.querySelector(".lightbox-close");

  if (lightbox && lightboxImg) {
    document.querySelectorAll(".lightbox-trigger").forEach(function (thumb) {
      thumb.addEventListener("click", function () {
        lightboxImg.src = thumb.getAttribute("data-full") || thumb.src;
        lightbox.classList.add("is-open");
      });
    });

    function closeLightbox() {
      lightbox.classList.remove("is-open");
      lightboxImg.src = "";
    }

    if (lightboxClose) lightboxClose.addEventListener("click", closeLightbox);
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) closeLightbox();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeLightbox();
    });
  }
});
