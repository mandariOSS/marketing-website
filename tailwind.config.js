/** @type {import('tailwindcss').Config} */

// ── Theme für Tailwind CSS 4 ─────────────────────────────────────────────
// static/css/input.css lädt diese Datei mit @config. Dort stehen auch die Quellen (@source), die Safelist
// (@source inline), der dunkle Modus und die Hover-Variante; Tailwind 4 liest content und safelist nicht mehr
// aus der JS-Konfiguration.
//
// Farben wie in Tailwind 3: Tailwind 4 bringt eine neue Palette in OKLCH mit kräftigeren, leicht verschobenen
// Tönen. Die Website behält ihre Hexwerte (Gestaltungssystem: Tinte #111827, Text #4B5563 …), deshalb stehen die
// verwendeten Farbfamilien hier mit den Werten von Tailwind 3. Wer eine weitere Familie verwendet, ergänzt sie
// hier, sonst gilt für sie die neue Palette.
const farben = {
  gray: { 50: '#f9fafb', 100: '#f3f4f6', 200: '#e5e7eb', 300: '#d1d5db', 400: '#9ca3af', 500: '#6b7280', 600: '#4b5563', 700: '#374151', 800: '#1f2937', 900: '#111827', 950: '#030712' },
  red: { 50: '#fef2f2', 100: '#fee2e2', 200: '#fecaca', 300: '#fca5a5', 400: '#f87171', 500: '#ef4444', 600: '#dc2626', 700: '#b91c1c', 800: '#991b1b', 900: '#7f1d1d', 950: '#450a0a' },
  orange: { 50: '#fff7ed', 100: '#ffedd5', 200: '#fed7aa', 300: '#fdba74', 400: '#fb923c', 500: '#f97316', 600: '#ea580c', 700: '#c2410c', 800: '#9a3412', 900: '#7c2d12', 950: '#431407' },
  amber: { 50: '#fffbeb', 100: '#fef3c7', 200: '#fde68a', 300: '#fcd34d', 400: '#fbbf24', 500: '#f59e0b', 600: '#d97706', 700: '#b45309', 800: '#92400e', 900: '#78350f', 950: '#451a03' },
  green: { 50: '#f0fdf4', 100: '#dcfce7', 200: '#bbf7d0', 300: '#86efac', 400: '#4ade80', 500: '#22c55e', 600: '#16a34a', 700: '#15803d', 800: '#166534', 900: '#14532d', 950: '#052e16' },
  teal: { 50: '#f0fdfa', 100: '#ccfbf1', 200: '#99f6e4', 300: '#5eead4', 400: '#2dd4bf', 500: '#14b8a6', 600: '#0d9488', 700: '#0f766e', 800: '#115e59', 900: '#134e4a', 950: '#042f2e' },
  blue: { 50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe', 300: '#93c5fd', 400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af', 900: '#1e3a8a', 950: '#172554' },
  rose: { 50: '#fff1f2', 100: '#ffe4e6', 200: '#fecdd3', 300: '#fda4af', 400: '#fb7185', 500: '#f43f5e', 600: '#e11d48', 700: '#be123c', 800: '#9f1239', 900: '#881337', 950: '#4c0519' },
};
const grau = farben.gray;

// Prosa ohne Rundungsfehler: Tailwind 4 verkleinert mit Lightning CSS, das Zahlen auf sechs gültige Stellen kürzt. Aus
// 1.3333333em (Plugin) würde 1.33333em, bei 18 px also 23,99994 statt 24 px; der Browser rundet Abstände ab, Text
// rutscht um einen Pixel und zweispaltige Listen brechen anders um. prose-lg hat die Grundgröße 18 px (1.125rem),
// darum stehen ihre Abstände hier in rem: dieselben Werte wie im Plugin, nur exakt (18 px × 1.3333333 = 24 px = 1.5rem).
// Zeilenhöhen ohne Einheit in prose: auf sechs Stellen aufgerundet (40 px statt 39,99996 px). Die Einrückung der
// Listenpunkte (0.4444444em) bleibt beim Plugin: Gekürzt landet sie wie bisher auf demselben Bildpunkt.
const exakt = {
  DEFAULT: {
    h1: { lineHeight: '1.11112' }, // 1.1111111
    h2: { lineHeight: '1.33334' }, // 1.3333333
    figcaption: { lineHeight: '1.42858' }, // 1.4285714
  },
  lg: {
    p: { marginTop: '1.5rem', marginBottom: '1.5rem' }, // 1.3333333em
    '[class~="lead"]': { fontSize: '1.375rem', marginTop: '1.5rem', marginBottom: '1.5rem' }, // 1.2222222em, 1.0909091em
    blockquote: { marginTop: '1.875rem', marginBottom: '1.875rem' }, // 1.6666667em
    h1: { fontSize: '3rem', marginBottom: '2.5rem' }, // 2.6666667em, 0.8333333em
    img: { marginTop: '2rem', marginBottom: '2rem' }, // 1.7777778em
    picture: { marginTop: '2rem', marginBottom: '2rem' },
    video: { marginTop: '2rem', marginBottom: '2rem' },
    figure: { marginTop: '2rem', marginBottom: '2rem' },
    ol: { marginTop: '1.5rem', marginBottom: '1.5rem', paddingInlineStart: '1.75rem' }, // 1.3333333em, 1.5555556em
    ul: { marginTop: '1.5rem', marginBottom: '1.5rem', paddingInlineStart: '1.75rem' },
    li: { marginTop: '0.75rem', marginBottom: '0.75rem' }, // 0.6666667em
    '> ul > li p': { marginTop: '1rem', marginBottom: '1rem' }, // 0.8888889em
    '> ul > li > p:first-child': { marginTop: '1.5rem' },
    '> ul > li > p:last-child': { marginBottom: '1.5rem' },
    '> ol > li > p:first-child': { marginTop: '1.5rem' },
    '> ol > li > p:last-child': { marginBottom: '1.5rem' },
    'ul ul, ul ol, ol ul, ol ol': { marginTop: '1rem', marginBottom: '1rem' }, // 0.8888889em
    dl: { marginTop: '1.5rem', marginBottom: '1.5rem' },
    dt: { marginTop: '1.5rem' },
    dd: { marginTop: '0.75rem', paddingInlineStart: '1.75rem' },
    hr: { marginTop: '3.5rem', marginBottom: '3.5rem' }, // 3.1111111em
  },
};

module.exports = {
  theme: {
    extend: {
      colors: {
        ...farben,
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
      // Schriftgrößen und Haltepunkte wie in Tailwind 3: Zeilenhöhen in rem (Tailwind 4: Faktoren, die sich anders
      // vererben) und Haltepunkte in px wie die Medienabfragen in input.css (Tailwind 4: rem).
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.75rem' }],
        xl: ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
        '7xl': ['4.5rem', { lineHeight: '1' }],
        '8xl': ['6rem', { lineHeight: '1' }],
        '9xl': ['8rem', { lineHeight: '1' }],
      },
      screens: { sm: '640px', md: '768px', lg: '1024px', xl: '1280px', '2xl': '1536px' },
      fontFamily: {
        sans: ['Inter', 'Inter Ersatz', 'Inter Ersatz Roboto', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      // Rich Text (Prosa) auf der Skala des Gestaltungssystems: Text #4B5563, Überschriften 28/22/18 px,
      // Aufzählungspunkte wie in den Bausteinen. Links gestaltet static/css/input.css (eine Linkgestalt).
      // Die übrigen Prosa-Farben nimmt das Plugin aus der neuen Palette; hier stehen sie mit den Grautönen von oben.
      typography: {
        DEFAULT: {
          css: {
            '--tw-prose-body': '#4b5563',
            '--tw-prose-headings': grau[900],
            '--tw-prose-lead': grau[600],
            '--tw-prose-links': grau[900],
            '--tw-prose-bold': grau[900],
            '--tw-prose-counters': '#4b5563',
            '--tw-prose-bullets': '#9ca3af',
            '--tw-prose-hr': grau[200],
            '--tw-prose-quotes': grau[900],
            '--tw-prose-quote-borders': grau[200],
            '--tw-prose-captions': grau[500],
            '--tw-prose-kbd': grau[900],
            '--tw-prose-kbd-shadows': 'rgb(17 24 39 / 10%)',
            '--tw-prose-code': grau[900],
            '--tw-prose-pre-code': grau[200],
            '--tw-prose-pre-bg': grau[800],
            '--tw-prose-th-borders': grau[300],
            '--tw-prose-td-borders': grau[200],
            '--tw-prose-invert-body': '#d1d5db',
            '--tw-prose-invert-lead': grau[400],
            '--tw-prose-invert-counters': grau[400],
            '--tw-prose-invert-bullets': '#6b7280',
            '--tw-prose-invert-hr': grau[700],
            '--tw-prose-invert-quotes': grau[100],
            '--tw-prose-invert-quote-borders': grau[700],
            '--tw-prose-invert-captions': grau[400],
            '--tw-prose-invert-pre-code': grau[300],
            '--tw-prose-invert-th-borders': grau[600],
            '--tw-prose-invert-td-borders': grau[700],
            ...exakt.DEFAULT,
          },
        },
        lg: {
          css: {
            ...exakt.lg,
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
