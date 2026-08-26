/**
 * RaktDaan Dashboard Controller & Profile Data Binding
 */

document.addEventListener('DOMContentLoaded', () => {
  // Check auth session
  const token = RaktDaan.getToken();
  if (!token && (window.location.pathname.includes('/dashboard'))) {
    window.location.href = '/donor/login';
    return;
  }

  // Dashboard Tab Switcher
  const sidebarLinks = document.querySelectorAll('.sidebar-link[data-tab]');
  const tabContents = document.querySelectorAll('.dashboard-tab-content');

  sidebarLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const targetTab = this.dataset.tab;

      sidebarLinks.forEach(l => l.classList.remove('active'));
      this.classList.add('active');

      tabContents.forEach(tab => {
        if (tab.id === `tab-${targetTab}`) {
          tab.classList.remove('hidden');
        } else {
          tab.classList.add('hidden');
        }
      });
    });
  });
});
