import { describe, expect, it } from 'vitest'

import { parseAuthForm } from '@/schemas/auth/forms'

const VALID_EMAIL = 'user@example.com'
const VALID_PASSWORD = 'securepassword123'

describe('parseAuthForm', () => {
  describe.each(['login', 'signup'] as const)('variant: %s', (variant) => {
    it('succeeds with valid email and password', () => {
      const result = parseAuthForm(variant, {
        email: VALID_EMAIL,
        password: VALID_PASSWORD
      })
      expect(result.success).toBe(true)
    })

    it('fails with an invalid email', () => {
      const result = parseAuthForm(variant, {
        email: 'not-an-email',
        password: VALID_PASSWORD
      })
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.fieldErrors).toHaveProperty('email')
      }
    })

    it('fails with a password shorter than 8 characters', () => {
      const result = parseAuthForm(variant, {
        email: VALID_EMAIL,
        password: 'short'
      })
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.fieldErrors).toHaveProperty('password')
      }
    })

    it('fails when both fields are invalid and returns both errors', () => {
      const result = parseAuthForm(variant, {
        email: 'bad',
        password: 'tiny'
      })
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.fieldErrors).toHaveProperty('email')
        expect(result.fieldErrors).toHaveProperty('password')
      }
    })

    it('fails when data is empty object', () => {
      const result = parseAuthForm(variant, {})
      expect(result.success).toBe(false)
    })

    it('returns a single string per field (not an array)', () => {
      const result = parseAuthForm(variant, { email: 'bad', password: 'x' })
      expect(result.success).toBe(false)
      if (!result.success) {
        for (const value of Object.values(result.fieldErrors)) {
          expect(typeof value).toBe('string')
        }
      }
    })
  })
})
