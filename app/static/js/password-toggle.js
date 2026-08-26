function togglePasswordVisibility(inputId, btn) {
  const input = document.getElementById(inputId);
  if (input) {
    const isPass = input.type === 'password';
    input.type = isPass ? 'text' : 'password';
    btn.innerText = isPass ? '🔒' : '👁️';
  }
}
