'use client'

import Link from 'next/link'
import { FormEvent, startTransition, useActionState, useState } from 'react'

import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel
} from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { parseAuthForm } from '@/schemas/auth/forms'
import { AuthFormProps, AuthFormVariant } from '@/types/auth/types'

export const AuthForm = ({
  title,
  submitLabel,
  submittingLabel,
  action,
  redirectPath
}: AuthFormProps) => {
  const variant: AuthFormVariant = title === 'Login' ? 'login' : 'signup'
  const [state, formAction, isPending] = useActionState(action, null)
  const signUpHref = `/signup?next=${encodeURIComponent('/login')}`

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFieldErrors({})

    const formData = new FormData(event.currentTarget)
    const rawFormData = Object.fromEntries(formData.entries())

    const parseResult = parseAuthForm(variant, rawFormData)

    if (!parseResult.success) {
      setFieldErrors(parseResult.fieldErrors)
      return
    }

    startTransition(() => {
      formAction(formData)
    })
  }

  return (
    <main className="mx-auto flex w-full max-w-md items-center justify-center p-6">
      <section className="w-full rounded-xl border p-6 shadow-sm">
        <h1 className="mb-6 text-2xl font-semibold">{title}</h1>

        <form method="post" onSubmit={handleSubmit} className="space-y-4">
          <Input type="hidden" name="redirectPath" value={redirectPath} />
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

          {state?.error && (
            <p className="text-destructive text-sm">{state.error}</p>
          )}

          <button
            type="submit"
            disabled={isPending}
            className={
              'bg-primary text-primary-foreground hover:text-primary hover:border-primary w-full rounded-md border px-4 py-2 font-semibold transition-colors hover:cursor-pointer hover:border hover:bg-transparent disabled:opacity-60'
            }
          >
            {isPending ? submittingLabel : submitLabel}
          </button>
        </form>

        {(title === 'Login' && (
          <p className="mt-4 text-center text-sm">
            Don&apos;t have an account?{' '}
            <Link
              href={signUpHref}
              className="text-primary animated-border-bottom font-semibold"
            >
              Sign up
            </Link>
          </p>
        )) ||
          (title === 'Sign Up' && (
            <p className="mt-4 text-center text-sm">
              Already have an account?{' '}
              <Link
                href={redirectPath}
                className="text-primary animated-border-bottom font-semibold"
              >
                Login
              </Link>
            </p>
          ))}
      </section>
    </main>
  )
}
