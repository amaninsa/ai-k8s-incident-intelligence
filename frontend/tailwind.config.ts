import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(99, 102, 241, 0.5)",
        "glow-lg": "0 0 60px -15px rgba(99, 102, 241, 0.55)",
        "glow-sm": "0 0 24px -8px rgba(59, 130, 246, 0.35)",
        card: "0 24px 80px -32px rgba(0, 0, 0, 0.75)",
      },
      backgroundImage: {
        "grid-pattern":
          "linear-gradient(to right, rgba(148, 163, 184, 0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(148, 163, 184, 0.05) 1px, transparent 1px)",
        "auth-mesh":
          "radial-gradient(circle at 20% 20%, rgba(59,130,246,0.15), transparent 35%), radial-gradient(circle at 80% 30%, rgba(139,92,246,0.12), transparent 30%), radial-gradient(circle at 50% 80%, rgba(14,165,233,0.08), transparent 40%)",
      },
      animation: {
        "pulse-soft": "pulse-soft 2.4s ease-in-out infinite",
        shimmer: "shimmer 2.5s linear infinite",
        "fade-up": "fade-up 0.5s ease-out",
      },
      keyframes: {
        "pulse-soft": {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "1" },
        },
        shimmer: {
          "0%": { backgroundPosition: "200% 0" },
          "100%": { backgroundPosition: "-200% 0" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
