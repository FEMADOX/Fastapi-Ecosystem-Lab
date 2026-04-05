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

const appCodeFiles = ['src/app/**/*.{ts,tsx,js,mjs,cjs}']
const appReactFiles = ['src/app/**/*.{tsx,jsx}']

const scopeConfigToFiles = (config, files) => ({
  ...config,
  files
})

const scopeConfigsToFiles = (configs, files) => {
  const configList = Array.isArray(configs) ? configs : [configs]
  return configList.map((config) => scopeConfigToFiles(config, files))
}

const ignoresLintingConfig = defineConfig([
  globalIgnores([
    '.next/',
    'node_modules/',
    'next-env.d.ts',
    '.agents/**',
    'src/components/**',
    'src/lib/**',
  ])
])

const languageLintingConfig = defineConfig([
  {
    files: appCodeFiles,
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
  scopeConfigToFiles(eslintJs.configs.recommended, appCodeFiles),
  ...scopeConfigsToFiles(tseslint.configs.recommendedTypeChecked, appCodeFiles),
  ...scopeConfigsToFiles(compat.extends('standard'), appCodeFiles),
  {
    files: appCodeFiles,
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
    files: appReactFiles,
    settings: {
      react: {
        version: 'detect'
      }
    }
  },
  ...scopeConfigsToFiles(eslintPluginReact.configs.flat.recommended, appReactFiles),
  ...scopeConfigsToFiles(eslintPluginReact.configs.flat['jsx-runtime'], appReactFiles),
  ...scopeConfigsToFiles(
    eslintReact.configs['recommended-type-checked'],
    appReactFiles
  ),
  ...scopeConfigsToFiles(
    eslintPluginReactHooks.configs['recommended-latest'],
    appReactFiles
  ),
  {
    files: appReactFiles,
    rules: {
      '@eslint-react/no-useless-fragment': 'error',
      '@eslint-react/no-missing-key': 'warn',
      'react/no-array-index-key': 'off'
    }
  }
])

const reactA11yLintingConfig = defineConfig([
  {
    files: appReactFiles
  },
  ...scopeConfigsToFiles(
    eslintPluginJsxA11y.flatConfigs.recommended,
    appReactFiles
  ),
  {
    files: appReactFiles,
    rules: {
      'jsx-a11y/click-events-have-key-events': 'off'
    }
  }
])

const nextLintingConfig = defineConfig([
  {
    files: appReactFiles
  },
  ...scopeConfigsToFiles(
    compat.extends('plugin:@next/next/recommended'),
    appReactFiles
  ),
  {
    files: appReactFiles,
    rules: {
      '@next/next/no-img-element': 'off'
    }
  }
])

export default defineConfig([
  ...ignoresLintingConfig,
  ...languageLintingConfig,
  ...reactLintingConfig,
  ...reactA11yLintingConfig,
  ...nextLintingConfig
])
