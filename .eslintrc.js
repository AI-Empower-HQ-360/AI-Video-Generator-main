module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
    jest: true
  },
  extends: [
    'eslint:recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    'no-unused-vars': 'warn',
    'no-console': 'off',
    'indent': ['error', 2],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always']
  },
  globals: {
    'bootstrap': 'readonly'
  },
  ignorePatterns: [
    'src/gurus/',
    'src/api/',
    'durable-deployment/',
    'tests/test_bojan_guru.js'
  ]
};