// MOCK DATA - REPLACE WITH MEMBER 4 API
const mockInventoryData = [
  { blood_group: 'A+', units: 45, repository: 'Central Hospital Mumbai', status: 'Available' },
  { blood_group: 'B+', units: 62, repository: 'Apex Center Delhi', status: 'Available' },
  { blood_group: 'O+', units: 88, repository: 'City Center Bengaluru', status: 'Available' },
  { blood_group: 'O-', units: 12, repository: 'Regional Repository Pune', status: 'Low Stock' },
  { blood_group: 'AB+', units: 28, repository: 'City Hospital Kolkata', status: 'Available' },
  { blood_group: 'A-', units: 8, repository: 'Metro Center Hyderabad', status: 'Low Stock' },
  { blood_group: 'B-', units: 5, repository: 'Central Hospital Mumbai', status: 'Critical' },
  { blood_group: 'AB-', units: 4, repository: 'Apex Center Delhi', status: 'Critical' }
];

function renderInventoryCards(data) {
  const container = document.getElementById('inventory-cards-container');
  if (!container) return;

  container.innerHTML = data.map(item => `
    <div class="card text-center hover-lift">
      <div class="blood-type-badge" style="margin: 0 auto 14px;">${item.blood_group}</div>
      <div class="font-heading" style="font-size: 2rem; font-weight: 800;">${item.units} Units</div>
      <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 12px;">${item.repository}</div>
      <span class="badge ${item.status === 'Available' ? 'badge-success' : 'badge-warning'}">${item.status}</span>
    </div>
  `).join('');
}

document.addEventListener('DOMContentLoaded', () => renderInventoryCards(mockInventoryData));
