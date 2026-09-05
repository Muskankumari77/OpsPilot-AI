import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",

  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
  ],

  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: "#F7F7FF",
          surface: "#FFFFFF",
          card: "#FFFFFF",
          soft: "#F1F0FF",
        },

        border: {
          DEFAULT: "#E7E4F2",
        },

        accent: {
          primary: "#6C4DFF",
          secondary: "#8B5CF6",
          pink: "#EC4FD8",
          blue: "#3B82F6",
          cyan: "#22C7E8",

          // Backward compatibility with existing components
          indigo: "#6C4DFF",
          violet: "#8B5CF6",
        },

        text: {
          primary: "#11142D",
          muted: "#6F728C",
          soft: "#9698AA",
        },

        status: {
          success: "#16B979",
          warning: "#F59E0B",
          danger: "#EF476F",
        },
      },

      fontFamily: {
        sans: [
          "var(--font-sans)",
          "Inter",
          "system-ui",
          "sans-serif",
        ],

        display: [
          "var(--font-display)",
          "Inter",
          "system-ui",
          "sans-serif",
        ],
      },

      borderRadius: {
        card: "1.25rem",
        xl: "1.5rem",
        "2xl": "2rem",
        "3xl": "2.25rem",
      },

      boxShadow: {
        soft:
          "0 10px 40px rgba(76, 61, 150, 0.08)",

        glow:
          "0 15px 50px rgba(108, 77, 255, 0.20)",

        "glow-pink":
          "0 15px 50px rgba(236, 79, 216, 0.18)",
      },
    },
  },

  plugins: [],
};

export default config;