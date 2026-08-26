document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.mobile-nav-toggle');
  const nav = document.querySelector('.navbar-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('active');
    });
  }
});
