import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './hooks/**/*.{ts,tsx}'],
  theme: {
    extend: {
      typography: {
        invert: {
          css: {
            '--tw-prose-body': '#d4d4d4',
            '--tw-prose-headings': '#ffffff',
            '--tw-prose-links': '#818cf8',
            '--tw-prose-bold': '#ffffff',
            '--tw-prose-code': '#ffffff',
          },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}

export default config

