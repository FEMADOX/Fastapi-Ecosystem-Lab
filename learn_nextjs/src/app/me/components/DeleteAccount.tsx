import { useActionState, useState } from 'react'
import { deleteAccountAction } from '@/actions/user/actions'
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Field,
  FieldError,
  FieldLabel,
  Input,
  PasswordInput
} from '@/components/ui'
import ProfileUpdateForm from './ProfileUpdateForm'

export const DeleteAccountComponent = () => {
  const [deleteState, deleteFormAction, isDeletePending] = useActionState(
    deleteAccountAction,
    null
  )
  const [deleteConfirmation, setDeleteConfirmation] = useState('')

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-destructive">Delete Account</CardTitle>
      </CardHeader>
      <CardContent>
        <Dialog>
          <div className="flex flex-col gap-4">
            <Field>
              <FieldLabel htmlFor="confirmDelete">
                Type <strong>DELETE</strong> to confirm
              </FieldLabel>
              <Input
                id="confirmDelete"
                name="confirmDelete"
                value={deleteConfirmation}
                onChange={(event) => setDeleteConfirmation(event.target.value)}
                required
              />
              <FieldError>This action is irreversible.</FieldError>
            </Field>

            <DialogTrigger
              render={
                <Button
                  type="button"
                  variant="destructive"
                  disabled={deleteConfirmation !== 'DELETE'}
                  className="w-full cursor-pointer"
                />
              }
            >
              Delete My Account
            </DialogTrigger>
          </div>

          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Account</DialogTitle>
              <DialogDescription>
                This action will permanently remove your account and all
                associated data. Enter your current password to continue.
              </DialogDescription>
            </DialogHeader>

            <ProfileUpdateForm
              action={deleteFormAction}
              state={deleteState}
              isPending={isDeletePending}
              submitLabel="Delete My Account"
              pendingLabel="Deleting..."
              submitVariant="destructive"
            >
              <input type="hidden" name="confirmDelete" value="DELETE" />
              <Field>
                <FieldLabel htmlFor="deleteCurrentPassword">
                  Current password
                </FieldLabel>
                <PasswordInput
                  id="deleteCurrentPassword"
                  name="currentPassword"
                  placeholder="Your password"
                  required
                />
              </Field>
            </ProfileUpdateForm>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  )
}
