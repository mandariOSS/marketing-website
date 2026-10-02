/** @type {import('tailwindcss').Config} */

// ── Safelist für dynamisch zusammengesetzte Klassen ──────────────────────
// Die StreamField-Block-Templates bauen Farbklassen zur Laufzeit zusammen
// (z. B. `bg-{{ card.color }}-600` in _mandari_card.html). Der Tailwind-
// Scanner sieht nur den Template-Quelltext und kann solche Klassen nicht
// erkennen — ohne Safelist fehlen sie im kompilierten CSS (purged) und
// Buttons/Icons erscheinen unstyled. Hier werden deshalb alle Kombinationen
// aus Palette (COLOR_CHOICES in marketing/blocks.py) und den in den
// Block-Templates verwendeten Utility+Shade-Varianten explizit erzeugt.
const paletteColors = ['primary', 'green', 'blue', 'amber', 'rose', 'teal', 'gray'];

const dynamicColorClasses = paletteColors.flatMap((c) => [
  // Hintergründe (Cards, Icons, Badges, Buttons)
  `bg-${c}-50`, `bg-${c}-100`, `bg-${c}-600`,
  `hover:bg-${c}-700`,
  `dark:bg-${c}-900/20`, `dark:bg-${c}-900/30`, `dark:bg-${c}-900/50`,
  // Rahmen (Cards, Stats, Pricing-Highlight)
  `border-${c}-200`, `border-${c}-500`,
  `dark:border-${c}-500`, `dark:border-${c}-800`,
  `hover:border-${c}-300`, `dark:hover:border-${c}-700`,
  // Text (Icons, Badges, Subtitles, Step-Nummern)
  `text-${c}-200`, `text-${c}-300`, `text-${c}-400`, `text-${c}-500`,
  `text-${c}-600`, `text-${c}-700`, `text-${c}-800`,
  `dark:text-${c}-300`, `dark:text-${c}-400`, `dark:text-${c}-800`,
  // Gradients (Hero, Gradient-CTA)
  `from-${c}-50`, `from-${c}-600`, `to-${c}-800`,
]);

// Dynamische Grid-Spalten (pricing_table: lg:grid-cols-{{ tiers|length }},
// stats_grid: md:grid-cols-{{ columns }})
const dynamicGridClasses = [
  'md:grid-cols-2', 'md:grid-cols-3', 'md:grid-cols-4',
  'lg:grid-cols-2', 'lg:grid-cols-3', 'lg:grid-cols-4',
];

module.exports = {
  content: [
    "./templates/**/*.html",
    "./marketing/templates/**/*.html",
    "./blog/templates/**/*.html",
    "./.legal-content/**/*.html",
  ],
  safelist: [...dynamicColorClasses, ...dynamicGridClasses],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      // Rich Text (Prosa) auf der Skala des Gestaltungssystems: Text #4B5563, Überschriften 28/22/18 px,
      // Aufzählungspunkte wie in den Bausteinen. Links gestaltet static/css/input.css (eine Linkgestalt).
      typography: {
        DEFAULT: {
          css: {
            '--tw-prose-body': '#4b5563',
            '--tw-prose-bullets': '#9ca3af',
            '--tw-prose-counters': '#4b5563',
            '--tw-prose-invert-body': '#d1d5db',
            '--tw-prose-invert-bullets': '#6b7280',
          },
        },
        lg: {
          css: {
            h2: { fontSize: '1.75rem', lineHeight: '1.2', letterSpacing: '-0.02em', fontWeight: '630', marginTop: '2.25em', marginBottom: '0.75em' },
            h3: { fontSize: '1.375rem', lineHeight: '1.3', letterSpacing: '-0.014em', fontWeight: '620', marginTop: '1.75em', marginBottom: '0.5em' },
            h4: { fontSize: '1.125rem', lineHeight: '1.4', fontWeight: '620', marginTop: '1.5em', marginBottom: '0.5em' },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
