document.addEventListener('DOMContentLoaded', () => {
  const links = document.querySelectorAll('.sidebar-link[data-tab]');
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const tabId = link.getAttribute('data-tab');
      
      links.forEach(l => l.classList.remove('active'));
      link.classList.add('active');

      const contents = document.querySelectorAll('.dashboard-tab-content');
      contents.forEach(c => c.classList.add('hidden'));

      const target = document.getElementById(`tab-${tabId}`);
      if (target) target.classList.remove('hidden');
    });
  });
});
