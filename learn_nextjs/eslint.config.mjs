import { FlatCompat } from '@eslint/eslintrc'
import { defineConfig, globalIgnores } from 'eslint/config'
import tseslint from 'typescript-eslint'
import eslintJs from '@eslint/js'
import eslintReact from '@eslint-react/eslint-plugin'
import eslintPluginReactHooks from 'eslint-plugin-react-hooks'
import eslintPluginJsxA11y from 'eslint-plugin-jsx-a11y'
import eslintPluginReact from 'eslint-plugin-react'

const compat = new FlatCompat({
  baseDirectory: import.meta.dirname
})

const ignoresLintingConfig = defineConfig([
  globalIgnores(['.next/', 'node_modules/', 'next-env.d.ts'])
])

const languageLintingConfig = defineConfig([
  {
    files: ['**/*.{ts,tsx,js,mjs,cjs}'],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        projectService: {
          allowDefaultProject: ['*.js', '*.mjs', '*.cjs']
        },
        tsconfigRootDir: import.meta.dirname
      }
    }
  },
  eslintJs.configs.recommended,
  tseslint.configs.recommendedTypeChecked,
  compat.extends('standard'),
  {
    settings: {
      'import/resolver': {
        typescript: true,
        node: true
      }
    },
    rules: {
      '@typescript-eslint/require-await': 'off',
      'no-console': ['warn', { allow: ['error'] }],
      '@typescript-eslint/no-unused-vars': [
        'warn',
        {
          args: 'after-used',
          ignoreRestSiblings: false,
          argsIgnorePattern: '^_.*?$',
          caughtErrorsIgnorePattern: '^_.*?$'
        }
      ],
      '@typescript-eslint/no-unsafe-member-access': 'off',
      '@typescript-eslint/no-confusing-void-expression': 'off',
      '@typescript-eslint/ban-ts-comment': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-inferrable-types': 'off',
      'import/no-unresolved': 'off',
      'n/no-missing-import': 'off'
    }
  }
])

const reactLintingConfig = defineConfig([
  {
    files: ['**/*.{tsx,jsx}'],
    settings: {
      react: {
        version: 'detect'
      }
    }
  },
  eslintPluginReact.configs.flat.recommended,
  eslintPluginReact.configs.flat['jsx-runtime'],
  eslintReact.configs['recommended-type-checked'],
  eslintPluginReactHooks.configs['recommended-latest'],
  {
    rules: {
      '@eslint-react/no-useless-fragment': 'error',
      '@eslint-react/no-missing-key': 'warn',
      'react/no-array-index-key': 'off'
    }
  }
])

const reactA11yLintingConfig = defineConfig([
  {
    files: ['**/*.{tsx,jsx}']
  },
  eslintPluginJsxA11y.flatConfigs.recommended,
  {
    rules: {
      'jsx-a11y/click-events-have-key-events': 'off'
    }
  }
])

const nextLintingConfig = defineConfig([
  {
    files: ['**/*.{tsx,jsx}']
  },
  compat.extends('plugin:@next/next/recommended'),
  {
    rules: {
      '@next/next/no-img-element': 'off'
    }
  }
])

export default defineConfig([
  ignoresLintingConfig,
  languageLintingConfig,
  reactLintingConfig,
  reactA11yLintingConfig,
  nextLintingConfig
])
