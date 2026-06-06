import { z } from 'zod'

export const stringFromForm = (message: string) =>
  z.preprocess(
    (value) => (typeof value === 'string' ? value.trim() : ''),
    z.string().min(1, message)
  )

export const nonNegativeNumberFromForm = (message: string) =>
  z.preprocess((value) => {
    if (typeof value !== 'string') {
      return Number.NaN
    }

    const normalizedValue = value.trim()
    if (normalizedValue.length === 0) {
      return Number.NaN
    }

    const numericValue = Number(normalizedValue)
    return Number.isFinite(numericValue) ? numericValue : Number.NaN
  }, z.number().nonnegative(message))
