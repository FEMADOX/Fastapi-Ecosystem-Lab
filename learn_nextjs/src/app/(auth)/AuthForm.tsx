'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  startTransition,
  useActionState,
  useEffect,
  useRef,
  useState
} from 'react'
import { toast } from 'sonner'
import {
  Button,
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
  Form,
  Input
} from '@/components/ui'
import { parseAuthForm } from '@/schemas/auth/forms'
import type { AuthFormProps, AuthFormVariant } from '@/types/auth/types'
import type { FormSubmitEvent } from '../items/new/types'

export const AuthForm = ({
  title,
  submitLabel,
  submittingLabel,
  action,
  redirectPath
}: AuthFormProps) => {
  const router = useRouter()
  const variant: AuthFormVariant = title === 'Login' ? 'login' : 'signup'
  const [state, formAction, isPending] = useActionState(action, null)
  const signUpHref = `/signup?next=${encodeURIComponent('/login')}`

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const pendingActionRef = useRef(false)

  useEffect(() => {
    if (!state || 'error' in state || !('success' in state)) return
    if (!pendingActionRef.current) return
    pendingActionRef.current = false

    const message =
      variant === 'login'
        ? 'Welcome back! You are now logged in.'
        : 'Welcome! Account created successfully.'

    router.push(state.redirectTo)
    router.refresh()
    toast.success(message)
  }, [router, state, variant])

  const handleSubmit = (event: FormSubmitEvent) => {
    event.preventDefault()
    setFieldErrors({})

    const formData = new FormData(event.currentTarget)
    const rawFormData = Object.fromEntries(formData.entries())

    const parseResult = parseAuthForm(variant, rawFormData)

    if (!parseResult.success) {
      setFieldErrors(parseResult.fieldErrors)
      return
    }

    pendingActionRef.current = true
    startTransition(() => {
      formAction(formData)
    })
  }

  return (
    <main className="mx-auto flex w-full max-w-md items-center justify-center p-6">
      <section className="card">
        <h1 className="mb-6 text-2xl font-semibold">{title}</h1>

        <Form method="post" onSubmit={handleSubmit}>
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

          {state && 'error' in state && state.error && (
            <p className="text-destructive text-sm">{state.error}</p>
          )}

          <Button
            type="submit"
            disabled={isPending}
            className="w-full cursor-pointer font-semibold"
          >
            {isPending ? submittingLabel : submitLabel}
          </Button>
        </Form>

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
