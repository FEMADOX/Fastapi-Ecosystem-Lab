import { describe, expect, it } from 'vitest'
import { getSafeNextPath } from '@/app/(auth)/getSafeNextPath'

describe('getSafeNextPath', () => {
  describe('returns "/" for unsafe or missing inputs', () => {
    it('returns "/" when called with no argument', () => {
      expect(getSafeNextPath()).toBe('/')
    })

    it('returns "/" for empty string', () => {
      expect(getSafeNextPath('')).toBe('/')
    })

    it('returns "/" for an external http URL', () => {
      expect(getSafeNextPath('http://evil.com')).toBe('/')
    })

    it('returns "/" for an external https URL', () => {
      expect(getSafeNextPath('https://evil.com/steal')).toBe('/')
    })

    it('returns "/" for a protocol-relative URL (//)', () => {
      expect(getSafeNextPath('//evil.com')).toBe('/')
    })

    it('returns "/" for a string that does not start with "/"', () => {
      expect(getSafeNextPath('evil.com/path')).toBe('/')
    })
  })

  describe('returns the path for safe internal paths', () => {
    it('returns "/" for the root path', () => {
      expect(getSafeNextPath('/')).toBe('/')
    })

    it('returns the path for a valid internal path', () => {
      expect(getSafeNextPath('/items')).toBe('/items')
    })

    it('returns the path with nested segments', () => {
      expect(getSafeNextPath('/items/123')).toBe('/items/123')
    })

    it('preserves query strings in safe paths', () => {
      expect(getSafeNextPath('/items?page=1')).toBe('/items?page=1')
    })
  })

  describe('handles array input', () => {
    it('returns the first element when it is a safe path', () => {
      expect(getSafeNextPath(['/dashboard', '/items'])).toBe('/dashboard')
    })

    it('returns "/" when the first element is an external URL', () => {
      expect(getSafeNextPath(['http://evil.com', '/items'])).toBe('/')
    })

    it('returns "/" for an empty array', () => {
      expect(getSafeNextPath([])).toBe('/')
    })
  })
})
