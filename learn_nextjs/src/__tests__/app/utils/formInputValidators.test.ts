import { describe, expect, it } from 'vitest'
import { z } from 'zod'

import {
  nonNegativeNumberFromForm,
  nullableImageUrlFromForm,
  stringFromForm
} from '@/app/utils/formInputValidators'

// Helper to parse a single value through a zod schema
const parse = (schema: z.ZodTypeAny, value: unknown) => schema.safeParse(value)

describe('stringFromForm', () => {
  const schema = stringFromForm('Name is required')

  it('passes for a non-empty string', () => {
    const result = parse(schema, 'hello')
    expect(result.success).toBe(true)
    if (result.success) expect(result.data).toBe('hello')
  })

  it('trims leading and trailing whitespace', () => {
    const result = parse(schema, '  hello  ')
    expect(result.success).toBe(true)
    if (result.success) expect(result.data).toBe('hello')
  })

  it('fails for an empty string', () => {
    const result = parse(schema, '')
    expect(result.success).toBe(false)
  })

  it('fails for a whitespace-only string', () => {
    const result = parse(schema, '   ')
    expect(result.success).toBe(false)
  })

  it('coerces non-string values to empty string then fails', () => {
    const result = parse(schema, 42)
    expect(result.success).toBe(false)
  })

  it('includes the custom message on failure', () => {
    const result = parse(schema, '')
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('Name is required')
    }
  })
})

describe('nonNegativeNumberFromForm', () => {
  const schema = nonNegativeNumberFromForm(
    'Price must be a non-negative number'
  )

  it('parses a valid non-negative integer string', () => {
    const result = parse(schema, '10')
    expect(result.success).toBe(true)
    if (result.success) expect(result.data).toBe(10)
  })

  it('parses a valid float string', () => {
    const result = parse(schema, '9.99')
    expect(result.success).toBe(true)
    if (result.success) expect(result.data).toBe(9.99)
  })

  it('parses zero', () => {
    const result = parse(schema, '0')
    expect(result.success).toBe(true)
    if (result.success) expect(result.data).toBe(0)
  })

  it('fails for a negative number string', () => {
    const result = parse(schema, '-5')
    expect(result.success).toBe(false)
  })

  it('fails for an empty string', () => {
    const result = parse(schema, '')
    expect(result.success).toBe(false)
  })

  it('fails for a non-numeric string', () => {
    const result = parse(schema, 'abc')
    expect(result.success).toBe(false)
  })

  it('fails for a whitespace-only string', () => {
    const result = parse(schema, '   ')
    expect(result.success).toBe(false)
  })

  it('fails for a non-string non-number value', () => {
    const result = parse(schema, null)
    expect(result.success).toBe(false)
  })
})

describe('nullableImageUrlFromForm', () => {
  const schema = nullableImageUrlFromForm

  it('returns null for an empty string', () => {
    const result = parse(schema, '')
    expect(result.success).toBe(true)
    if (result.success) expect(result.data).toBeNull()
  })

  it('returns null for a whitespace-only string', () => {
    const result = parse(schema, '   ')
    expect(result.success).toBe(true)
    if (result.success) expect(result.data).toBeNull()
  })

  it('returns null for a non-string value', () => {
    const result = parse(schema, null)
    expect(result.success).toBe(true)
    if (result.success) expect(result.data).toBeNull()
  })

  it('passes for a valid URL', () => {
    const url = 'https://example.com/image.png'
    const result = parse(schema, url)
    expect(result.success).toBe(true)
    if (result.success) expect(result.data).toBe(url)
  })

  it('fails for an invalid URL string', () => {
    const result = parse(schema, 'not-a-url')
    expect(result.success).toBe(false)
  })
})
