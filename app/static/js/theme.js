const ThemeManager = {
  THEME_KEY: 'raktdaan_theme',

  init: () => {
    const savedTheme = localStorage.getItem(ThemeManager.THEME_KEY) || 'light';
    ThemeManager.setTheme(savedTheme);
  },

  setTheme: (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(ThemeManager.THEME_KEY, theme);
  },

  toggleTheme: () => {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'light' ? 'dark' : 'light';
    ThemeManager.setTheme(next);
  }
};

document.addEventListener('DOMContentLoaded', ThemeManager.init);
