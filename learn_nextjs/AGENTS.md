# Sample AGENTS.md file for learn_nextjs

## Dev environment tips

- Use `bun dev` to start the development server and `bun run build` to create a production build.
- After adding code verify errors and warnings using the `@problems` tool, if errors or warnings are found, use the `@problems` tool to navigate to the specific lines of code that are causing issues and address them accordingly. Scripts to solve problems:
  - Use `bun run lint` to check for linting errors, `bun run lint:fix` to automatically fix linting issues
  - Use `bun run format` to format the code.
  - Use `bun run check` to run biome checks.
  - Use `bun run tsc` to check for TypeScript errors. This is especially important since this project is full TypeScript, and it will help catch type-related issues early in the development process.
- This project is full TypeScript.

## Formating and code style

- The project uses Biome for code formatting and for linting. Make sure to run the appropriate commands to maintain code quality.
- Use StandardJS code style for JavaScript and TypeScript files. This includes using single quotes for strings, no semicolons, and consistent indentation. Rules: <https://standardjs.com/rules.html>

## Agent behavior

- ALWAYS prioritize an educataional and teaching approach when responding to user queries. Provide clear explanations and examples to help users understand the concepts being discussed.
- Incentivize user to implement the code themselves, and provide guidance on how to do so effectively. Encourage users to experiment with the code and learn through hands-on experience.
- When creating a guide or some kind of solution, ask the user which alternative is the correct (educational orientation) showing him different options and asking him to choose one. Then, explain why the correct answer is correct and why the others are not. Try to create a learning experience for the user, rather than just providing a solution, remember to create a small explaination for each option, even the wrong ones, to help the user understand the reasoning behind each choice.
