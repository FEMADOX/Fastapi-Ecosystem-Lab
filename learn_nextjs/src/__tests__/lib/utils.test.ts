import { describe, expect, it } from 'vitest'
import { cn } from '@/lib/utils'

describe('cn', () => {
  it('returns a single class unchanged', () => {
    expect(cn('text-red-500')).toBe('text-red-500')
  })

  it('joins multiple classes', () => {
    expect(cn('px-4', 'py-2')).toBe('px-4 py-2')
  })

  it('ignores falsy values', () => {
    expect(cn('px-4', false, undefined, null, 'py-2')).toBe('px-4 py-2')
  })

  it('resolves Tailwind conflicts — last class wins', () => {
    expect(cn('px-4', 'px-6')).toBe('px-6')
  })

  it('resolves color conflicts', () => {
    expect(cn('text-red-500', 'text-blue-500')).toBe('text-blue-500')
  })

  it('handles conditional objects', () => {
    expect(cn({ 'font-bold': true, italic: false })).toBe('font-bold')
  })

  it('handles arrays of classes', () => {
    expect(cn(['text-sm', 'font-medium'])).toBe('text-sm font-medium')
  })

  it('returns empty string for no arguments', () => {
    expect(cn()).toBe('')
  })
})
