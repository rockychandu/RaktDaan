document.addEventListener('DOMContentLoaded', () => {
  const items = document.querySelectorAll('.accordion-header');
  items.forEach(item => {
    item.addEventListener('click', () => {
      const parent = item.parentElement;
      parent.classList.toggle('active');
    });
  });
});
