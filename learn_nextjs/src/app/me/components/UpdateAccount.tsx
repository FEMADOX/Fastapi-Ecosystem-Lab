import { useRouter } from 'next/navigation'
import { useActionState, useEffect } from 'react'
import {
  updateProfileEmailAction,
  updateProfilePasswordAction
} from '@/actions/user/actions'
import { KeyRoundIcon, MailIcon } from '@/components/ui'
import ProfileUpdateForm from './ProfileUpdateForm'
import type { UpdateAccountComponentProps } from './types'
import UpdateCard from './UpdateCard'

export const UpdateAccountComponent = ({
  userEmail
}: UpdateAccountComponentProps) => {
  const [emailState, emailFormAction, isEmailPending] = useActionState(
    updateProfileEmailAction,
    null
  )
  const [passwordState, passwordFormAction, isPasswordPending] = useActionState(
    updateProfilePasswordAction,
    null
  )
  const router = useRouter()

  useEffect(() => {
    if (emailState?.success || passwordState?.success) router.refresh()
  }, [emailState, passwordState, router])

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <UpdateCard
        title="Update Email"
        description={userEmail}
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
          userEmail={userEmail}
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
  )
}
