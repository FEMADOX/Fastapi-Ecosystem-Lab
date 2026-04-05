import { describe, expect, it } from 'vitest'

import { itemFormSchema } from '@/schemas/items/forms'

// Helper — simulates FormData entries converted to a plain object
const parse = (data: Record<string, unknown>) => itemFormSchema.safeParse(data)

const VALID_INPUT = {
  name: 'Running Shoes',
  description: 'Lightweight and durable',
  price: '49.99',
  tax: '5',
  imageUrl: '',
}

describe('itemFormSchema', () => {
  describe('valid inputs', () => {
    it('succeeds with all required fields and no image', () => {
      const result = parse(VALID_INPUT)
      expect(result.success).toBe(true)
    })

    it('transforms price and tax strings to numbers', () => {
      const result = parse(VALID_INPUT)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.price).toBe(49.99)
        expect(result.data.tax).toBe(5)
      }
    })

    it('transforms imageUrl empty string to undefined', () => {
      const result = parse(VALID_INPUT)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.image_url).toBeUndefined()
      }
    })

    it('accepts a valid image URL', () => {
      const result = parse({ ...VALID_INPUT, imageUrl: 'https://example.com/shoe.png' })
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.image_url).toBe('https://example.com/shoe.png')
      }
    })

    it('accepts zero for price and tax', () => {
      const result = parse({ ...VALID_INPUT, price: '0', tax: '0' })
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.price).toBe(0)
        expect(result.data.tax).toBe(0)
      }
    })

    it('trims whitespace from name and description', () => {
      const result = parse({ ...VALID_INPUT, name: '  Shoes  ', description: '  Nice  ' })
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.name).toBe('Shoes')
        expect(result.data.description).toBe('Nice')
      }
    })

    it('output does not contain id or user_id fields', () => {
      const result = parse(VALID_INPUT)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data).not.toHaveProperty('id')
        expect(result.data).not.toHaveProperty('user_id')
      }
    })
  })

  describe('invalid inputs', () => {
    it('fails when name is empty', () => {
      const result = parse({ ...VALID_INPUT, name: '' })
      expect(result.success).toBe(false)
    })

    it('fails when description is empty', () => {
      const result = parse({ ...VALID_INPUT, description: '' })
      expect(result.success).toBe(false)
    })

    it('fails when price is a negative number', () => {
      const result = parse({ ...VALID_INPUT, price: '-1' })
      expect(result.success).toBe(false)
    })

    it('fails when tax is a negative number', () => {
      const result = parse({ ...VALID_INPUT, tax: '-0.5' })
      expect(result.success).toBe(false)
    })

    it('fails when price is a non-numeric string', () => {
      const result = parse({ ...VALID_INPUT, price: 'free' })
      expect(result.success).toBe(false)
    })

    it('fails when imageUrl is present but not a valid URL', () => {
      const result = parse({ ...VALID_INPUT, imageUrl: 'not-a-url' })
      expect(result.success).toBe(false)
    })

    it('fails when required fields are missing', () => {
      const result = parse({})
      expect(result.success).toBe(false)
    })
  })
})
