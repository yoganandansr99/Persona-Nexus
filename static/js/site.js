(function () {
  var burger = document.getElementById("nxBurger");
  var nav = document.getElementById("nxNav");
  if (!burger || !nav) return;

  function setOpen(open) {
    nav.classList.toggle("is-open", open);
    burger.classList.toggle("is-open", open);
    burger.setAttribute("aria-expanded", open ? "true" : "false");
  }

  burger.addEventListener("click", function () {
    setOpen(!nav.classList.contains("is-open"));
  });

  nav.querySelectorAll("a").forEach(function (a) {
    a.addEventListener("click", function () {
      setOpen(false);
    });
  });
})();
