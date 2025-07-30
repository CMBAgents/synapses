import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
      maxWidth: {
        'lg': '95%', // Adjust this value as needed
        '2xl': '800px', // Custom max width for our chat container
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: '100%',
          },
        },
        dark: {
          css: {
            color: 'rgb(var(--foreground-rgb-dark))',
            a: {
              color: '#3b82f6',
              '&:hover': {
                color: '#60a5fa',
              },
            },
            h1: {
              color: 'rgb(var(--foreground-rgb-dark))',
            },
            h2: {
              color: 'rgb(var(--foreground-rgb-dark))',
            },
            h3: {
              color: 'rgb(var(--foreground-rgb-dark))',
            },
            h4: {
              color: 'rgb(var(--foreground-rgb-dark))',
            },
            code: {
              color: 'rgb(var(--foreground-rgb-dark))',
              backgroundColor: 'rgb(var(--code-bg-dark))',
            },
            'pre code': {
              backgroundColor: 'transparent',
            },
            pre: {
              color: 'rgb(var(--foreground-rgb-dark))',
              backgroundColor: 'rgb(var(--code-block-bg-dark))',
            },
            strong: {
              color: 'rgb(var(--foreground-rgb-dark))',
            },
            blockquote: {
              color: 'rgb(var(--foreground-rgb-dark))',
            },
            thead: {
              color: 'rgb(var(--foreground-rgb-dark))',
            },
            'thead th': {
              color: 'rgb(var(--foreground-rgb-dark))',
            },
            'tbody tr': {
              borderBottomColor: 'rgb(var(--border-color-dark))',
            },
            'tbody td': {
              color: 'rgb(var(--foreground-rgb-dark))',
            },
          },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')]
};

export default config;
