// Runs synchronously in <head> BEFORE first paint, so there is no light-mode flash.
(function () {
  try {
    var saved = localStorage.getItem('cp-theme');
    var dark = saved ? saved === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.classList.toggle('dark', dark);
  } catch (e) {}
})();
