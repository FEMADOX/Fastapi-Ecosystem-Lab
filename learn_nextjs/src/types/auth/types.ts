export type AuthActionState = { error: string } | null

export type AuthFormVariant = 'login' | 'signup'

export type AuthFormProps = {
  title: string
  submitLabel: string
  submittingLabel: string
  action: (
    prevState: AuthActionState,
    formData: FormData
  ) => Promise<AuthActionState>
  redirectPath: string
}

export type AuthPageProps = {
  searchParams: Promise<{ next?: string }>
}
