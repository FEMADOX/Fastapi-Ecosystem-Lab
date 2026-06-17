import { KeyRoundIcon, MailIcon } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useActionState, useEffect } from 'react'
import {
  deleteAccountAction,
  updateProfileEmailAction,
  updateProfilePasswordAction
} from '@/actions/user/actions'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Field,
  FieldError,
  FieldLabel,
  Input
} from '@/components/ui'
import ProfileUpdateForm from './ProfileUpdateForm'
import type { TabProfileProps } from './types'
import UpdateCard from './UpdateCard'

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
    <div className="flex flex-col gap-6">
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

      <div className="grid gap-6 md:grid-cols-2">
        <UpdateCard
          title="Update Email"
          description={user.email}
          content="Change the address used for sign-in and account messages."
          actionLabel="Update Email"
          dialogDescription="Use your current password to confirm this change."
          icon={MailIcon}
        >
          <ProfileUpdateForm
            action={emailFormAction}
            state={emailState}
            isPending={isEmailPending}
            submitLabel="Update Email"
            pendingLabel="Updating..."
            formVariant="email"
            userEmail={user.email}
          />
        </UpdateCard>

        <UpdateCard
          title="Update Password"
          description="Refresh your account credentials."
          content="Replace your password without expanding the full form inline."
          actionLabel="Update Password"
          dialogDescription="Enter your current password before choosing a new one."
          icon={KeyRoundIcon}
        >
          <ProfileUpdateForm
            action={passwordFormAction}
            state={passwordState}
            isPending={isPasswordPending}
            submitLabel="Update Password"
            pendingLabel="Updating..."
            formVariant="password"
          />
        </UpdateCard>
      </div>

      <Card className="border-red-200">
        <CardHeader>
          <CardTitle className="text-destructive">Delete Account</CardTitle>
        </CardHeader>
        <CardContent>
          <ProfileUpdateForm
            action={deleteFormAction}
            state={deleteState}
            isPending={isDeletePending}
            submitLabel="Delete My Account"
            pendingLabel="Deleting..."
            submitVariant="destructive"
          >
            <Field>
              <FieldLabel htmlFor="confirmDelete">
                Type <strong>DELETE</strong> to confirm
              </FieldLabel>
              <Input id="confirmDelete" name="confirmDelete" required />
              <FieldError>This action is irreversible.</FieldError>
            </Field>
          </ProfileUpdateForm>
        </CardContent>
      </Card>
    </div>
  )
}
