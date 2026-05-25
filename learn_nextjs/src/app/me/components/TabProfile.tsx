import { useRouter } from 'next/navigation'
import { useActionState, useEffect } from 'react'
import {
  deleteAccountAction,
  updateProfileEmailAction,
  updateProfilePasswordAction
} from '@/actions/user/actions'
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
  Input
} from '@/components/ui'
import { ActionFeedback } from '../ActionFeedback'
import type { TabProfileProps } from './types'

export const TabProfileComponent = ({ user, isActive }: TabProfileProps) => {
  const [emailState, emailFormAction, isEmailPending] = useActionState(
    updateProfileEmailAction,
    null
  )
  const [passwordState, passwordFormAction, isPasswordPending] = useActionState(
    updateProfilePasswordAction,
    null
  )
  const [deleteState, deleteFormAction, isDeletePending] = useActionState(
    deleteAccountAction,
    null
  )
  const router = useRouter()

  useEffect(() => {
    if (emailState?.success || passwordState?.success) router.refresh()
  }, [emailState, passwordState, router])

  if (!isActive) return null

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Account Overview</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm">
          <p>
            <strong>Email:</strong> {user.email}
          </p>
          <p>
            <strong>Role:</strong> {user.is_superuser ? 'Superuser' : 'User'}
          </p>
          <p>
            <strong>Status:</strong> {user.is_active ? 'Active' : 'Inactive'}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Update Email</CardTitle>
        </CardHeader>
        <CardContent>
          <form action={emailFormAction} className="space-y-4" noValidate>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="email">New Email</FieldLabel>
                <Input id="email" name="email" type="email" required />
              </Field>
              <Field>
                <FieldLabel htmlFor="currentPasswordForEmail">
                  Current Password
                </FieldLabel>
                <Input
                  id="currentPasswordForEmail"
                  name="currentPassword"
                  type="password"
                  required
                />
              </Field>
            </FieldGroup>

            <ActionFeedback state={emailState} />

            <Button
              type="submit"
              disabled={isEmailPending}
              className="cursor-pointer"
            >
              {isEmailPending ? 'Updating...' : 'Update Email'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Update Password</CardTitle>
        </CardHeader>
        <CardContent>
          <form action={passwordFormAction} className="space-y-4" noValidate>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="currentPasswordForPassword">
                  Current Password
                </FieldLabel>
                <Input
                  id="currentPasswordForPassword"
                  name="currentPassword"
                  type="password"
                  required
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="newPassword">New Password</FieldLabel>
                <Input
                  id="newPassword"
                  name="newPassword"
                  type="password"
                  required
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="confirmPassword">
                  Confirm New Password
                </FieldLabel>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  required
                />
              </Field>
            </FieldGroup>

            <ActionFeedback state={passwordState} />

            <Button
              type="submit"
              disabled={isPasswordPending}
              className="cursor-pointer"
            >
              {isPasswordPending ? 'Updating...' : 'Update Password'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card className="border-red-200">
        <CardHeader>
          <CardTitle className="text-destructive">Delete Account</CardTitle>
        </CardHeader>
        <CardContent>
          <form action={deleteFormAction} className="space-y-4" noValidate>
            <Field>
              <FieldLabel htmlFor="confirmDelete">
                Type <strong>DELETE</strong> to confirm
              </FieldLabel>
              <Input id="confirmDelete" name="confirmDelete" required />
              <FieldError>This action is irreversible.</FieldError>
            </Field>

            <ActionFeedback state={deleteState} />

            <Button
              type="submit"
              variant="destructive"
              disabled={isDeletePending}
              className="cursor-pointer"
            >
              {isDeletePending ? 'Deleting...' : 'Delete My Account'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
