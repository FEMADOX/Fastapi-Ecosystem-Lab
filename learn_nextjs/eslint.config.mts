import { dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import eslintJs from '@eslint/js'
import eslintReact from '@eslint-react/eslint-plugin'
import { FlatCompat } from '@eslint/eslintrc'
import eslintConfigPrettier from 'eslint-config-prettier/flat'
import { defineConfig, globalIgnores } from 'eslint/config'
import eslintPluginImportSort from 'eslint-plugin-simple-import-sort'
// @ts-ignore - No types available for this package
import eslintPluginJsxA11y from 'eslint-plugin-jsx-a11y'
import eslintPluginReact from 'eslint-plugin-react'
import eslintPluginReactHooks from 'eslint-plugin-react-hooks'
import type { Linter } from 'eslint'
import tseslint from 'typescript-eslint'

const dirnameFromImportMeta = dirname(fileURLToPath(import.meta.url))

const compat = new FlatCompat({
  baseDirectory: dirnameFromImportMeta
})

const srcAllFiles = ['src/**/*.{ts,tsx,js,mjs,cjs}']
const appCodeFiles = ['src/app/**/*.{ts,tsx,js,mjs,cjs}']
const appReactFiles = ['src/app/**/*.{tsx,jsx}']

type FlatConfigShape = Linter.Config

const scopeConfigToFiles = (config: FlatConfigShape, files: string[]) => ({
  ...config,
  files
})

const scopeConfigsToFiles = (
  configs: FlatConfigShape | FlatConfigShape[],
  files: string[]
) => {
  const configList = Array.isArray(configs) ? configs : [configs]
  return configList.map((config) => scopeConfigToFiles(config, files))
}

const reactHooksRecommendedLatest = (
  eslintPluginReactHooks as unknown as {
    configs: Record<string, FlatConfigShape | FlatConfigShape[]>
  }
).configs['recommended-latest']

const ignoresLintingConfig = defineConfig([
  globalIgnores([
    '.next/',
    'node_modules/',
    'next-env.d.ts',
    '.agents/**',
    'src/components/**',
    'src/lib/**'
  ])
])

const srcParserConfig = defineConfig([
  {
    files: srcAllFiles,
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        tsconfigRootDir: dirnameFromImportMeta
      }
    }
  }
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
        tsconfigRootDir: dirnameFromImportMeta
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
  ...scopeConfigsToFiles(
    eslintPluginReact.configs.flat.recommended,
    appReactFiles
  ),
  ...scopeConfigsToFiles(
    eslintPluginReact.configs.flat['jsx-runtime'],
    appReactFiles
  ),
  ...scopeConfigsToFiles(
    eslintReact.configs['recommended-type-checked'],
    appReactFiles
  ),
  ...scopeConfigsToFiles(
    reactHooksRecommendedLatest,
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

const importSortConfig = defineConfig([
  {
    files: srcAllFiles,
    plugins: {
      'simple-import-sort': eslintPluginImportSort
    },
    rules: {
      'simple-import-sort/imports': 'error',
      'simple-import-sort/exports': 'error'
    }
  }
])

export default defineConfig([
  ...ignoresLintingConfig,
  ...srcParserConfig,
  ...importSortConfig,
  ...languageLintingConfig,
  ...reactLintingConfig,
  ...reactA11yLintingConfig,
  ...nextLintingConfig,
  eslintConfigPrettier
])
