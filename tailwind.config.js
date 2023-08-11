/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.html"],
  theme: {
    extend: {colors: {
      'battercolor': 'var(--battercolor)',
      'bowlercolor': 'var(--bowlercolor)',
      'playercolor': 'var(--playercolor)',

    },
    fontFamily: {
      PlayfairDisplay: ['Playfair Display', 'serif'],
    },
  },
  },
  plugins: [],
}

