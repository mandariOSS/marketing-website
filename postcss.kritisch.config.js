// Kritisches CSS (npm run build:css): Tailwind mit tailwind.kritisch.config.js, danach scripts/kritisches_css.js.
// Die Tailwind-CLI setzt ihren eigenen Tailwind-Schritt an die Stelle von „tailwindcss“ und hängt Autoprefixer
// und die Verkleinerung (--minify) an, wie beim vollständigen styles.css.
module.exports = {
  plugins: [require('tailwindcss'), require('./scripts/kritisches_css.js')],
};
