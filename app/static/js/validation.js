const FormValidator = {
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE_REGEX: /^[6-9]\d{9}$/,

  isValidEmail: (email) => FormValidator.EMAIL_REGEX.test(String(email).trim().toLowerCase()),
  isValidPhone: (phone) => FormValidator.PHONE_REGEX.test(String(phone).trim()),

  validateInput: (inputElement) => {
    const val = inputElement.value.trim();
    let isValid = true;
    if (inputElement.type === 'email' && val) isValid = FormValidator.isValidEmail(val);
    if (inputElement.type === 'tel' && val) isValid = FormValidator.isValidPhone(val);
    return isValid;
  }
};
