/**
 * RaktDaan Home Page Interactive Functionality
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Blood Availability Renderer
  const bloodUI = new BloodAvailabilityUI('blood-availability-grid');
  bloodUI.render();

  // Blood group filter buttons
  const filterBtns = document.querySelectorAll('.blood-filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      filterBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      const group = this.dataset.group || 'ALL';
      bloodUI.render(group);
    });
  });

  // Interactive FAQ Accordion
  const faqQuestions = document.querySelectorAll('.faq-question');
  faqQuestions.forEach(q => {
    q.addEventListener('click', function() {
      const item = this.parentElement;
      const isActive = item.classList.contains('active');
      
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));
      
      if (!isActive) {
        item.classList.add('active');
      }
    });
  });
});
