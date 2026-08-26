const ModalController = {
  openModal: (modalId) => {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
  },
  closeModal: (modalId) => {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
  }
};
