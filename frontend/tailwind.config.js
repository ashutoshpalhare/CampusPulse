/** Tailwind CSS v3 build config for CampusPulse (compiled locally, no CDN). */
const defaultTheme = require("tailwindcss/defaultTheme");

module.exports = {
  darkMode: "class", // Alpine toggles the "dark" class on <html>
  content: [
    // Django templates (project-level and app-level)
    "./tracker/templates/**/*.html",
    "./templates/**/*.html",
    // Classes written in Python (crispy layout css_class, etc.)
    "./tracker/**/*.py",
    // JS that builds class strings (toast styles)
    "./static/js/*.js",
    // Classes injected by the crispy-tailwind package
    "./frontend/crispy-classes.html",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", ...defaultTheme.fontFamily.sans],
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
