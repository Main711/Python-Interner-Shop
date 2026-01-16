(function () {
  const menuBtn = document.getElementById("mobileMenuBtn");
  const menu = document.getElementById("mobileMenu");
  if (menuBtn && menu) {
    menuBtn.addEventListener("click", () => menu.classList.toggle("open"));
  }

  // Tabs on home mobile auth
  const tabs = document.querySelectorAll(".auth-tabs .tab");
  if (tabs.length) {
    tabs.forEach(btn => {
      btn.addEventListener("click", () => {
        tabs.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const target = btn.getAttribute("data-tab");
        document.getElementById("tab-login")?.classList.toggle("hidden", target !== "login");
        document.getElementById("tab-register")?.classList.toggle("hidden", target !== "register");
      });
    });
  }
})();
