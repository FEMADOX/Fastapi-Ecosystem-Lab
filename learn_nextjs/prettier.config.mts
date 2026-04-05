import { type Config } from 'prettier'

const config: Config = {
  semi: false,
  singleQuote: true,
  trailingComma: "none",
  tabWidth: 2,
  arrowParens: "always",
  printWidth: 80,
  plugins: [
    "prettier-plugin-tailwindcss"
  ],
}

export default config
