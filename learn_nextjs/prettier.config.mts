import { type Config } from 'prettier'

const config: Config = {
  ignores: ['node_modules/**', '.next/**', 'dist/**'],
  semi: false,
  singleQuote: true,
  trailingComma: "none",
  tabWidth: 2,
  arrowParens: "always",
  printWidth: 80,
  plugins: [
    "prettier-plugin-tailwindcss"
  ]
}

export default config
