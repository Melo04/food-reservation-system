var toggleButton = document.getElementById("navbar-toggle");
var mobileNavbar = document.getElementById("mobile-navbar");

toggleButton.addEventListener("click", function () {
  mobileNavbar.classList.toggle("hidden");
});
