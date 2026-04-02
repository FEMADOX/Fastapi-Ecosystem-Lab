'use client'

import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel
} from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { useRouter } from 'next/navigation'
import { FormEvent, useState } from 'react'
import { z } from 'zod'
import { AuthFormProps } from './interfaces'

export const AuthForm = ({
  title,
  submitLabel,
  submittingLabel,
  schema,
  actionApi,
  redirectPath
}: AuthFormProps) => {
  const router = useRouter()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [submitError, setSubmitError] = useState('')

  const submitForm = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFieldErrors({})
    setSubmitError('')

    const formData = new FormData(event.currentTarget)
    const rawFormData = Object.fromEntries(formData.entries())
    const parseResult = schema.safeParse(rawFormData)

    if (!parseResult.success) {
      const flattenedErrors = z.flattenError(parseResult.error).fieldErrors
      const nextFieldErrors = Object.fromEntries(
        Object.entries(flattenedErrors)
          .filter(
            ([, messages]) => Array.isArray(messages) && messages.length > 0
          )
          .map(([fieldName, messages]) => [
            fieldName,
            (messages as string[])[0] ?? 'Invalid value'
          ])
      )
      setFieldErrors(nextFieldErrors)
      return
    }

    setIsSubmitting(true)

    const parsed = parseResult.data as { email: string; password: string }
    const { data, error } = await actionApi(parsed.email, parsed.password)
    if (error && !data) {
      setSubmitError(error)
      return
    }

    router.push(redirectPath)
    router.refresh()
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    submitForm(event)
      .catch((error: unknown) => {
        console.error(`Auth error (${title}):`, error)
        setSubmitError(
          error instanceof Error
            ? error.message
            : 'Something went wrong. Please try again.'
        )
      })
      .finally(() => {
        setIsSubmitting(false)
      })
  }

  return (
    <main className="mx-auto flex w-full max-w-md items-center justify-center p-6">
      <section className="w-full rounded-xl border p-6 shadow-sm">
        <h1 className="mb-6 text-2xl font-semibold">{title}</h1>

        <form method="post" onSubmit={handleSubmit} className="space-y-4">
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="email">
                Email<span className="text-destructive">*</span>
              </FieldLabel>
              <Input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                aria-invalid={!!fieldErrors.email}
                onChange={(event) => setEmail(event.target.value)}
              />
              <FieldError>{fieldErrors.email}</FieldError>
            </Field>
            <Field>
              <FieldLabel htmlFor="password">
                Password<span className="text-destructive">*</span>
              </FieldLabel>
              <Input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                aria-invalid={!!fieldErrors.password}
                onChange={(event) => setPassword(event.target.value)}
              />
              <FieldError>{fieldErrors.password}</FieldError>
            </Field>
          </FieldGroup>

          {submitError && (
            <p className="text-sm text-destructive">{submitError}</p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className={`
              w-full rounded-md border bg-primary px-4 py-2 text-primary-foreground font-semibold
              disabled:opacity-60 transition-colors
              hover:cursor-pointer hover:bg-transparent hover:text-primary hover:border hover:border-primary
            `}
          >
            {isSubmitting ? submittingLabel : submitLabel}
          </button>
        </form>
      </section>
    </main>
  )
}
