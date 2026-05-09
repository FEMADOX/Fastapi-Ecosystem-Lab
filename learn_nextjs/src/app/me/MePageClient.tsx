'use client'

import Link from 'next/link'
import { useActionState, useState } from 'react'

import {
  deleteAccountAction,
  deleteOwnedItemAction,
  updateOwnedItemAction,
  updateProfileEmailAction,
  updateProfilePasswordAction
} from '@/actions/user/actions'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel
} from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { ActionFeedback } from './ActionFeedback'
import type { MePageClientProps, OwnedItemEditorProps } from './types'

const OwnedItemEditor = ({ item }: OwnedItemEditorProps) => {
  const [state, formAction, isPending] = useActionState(
    updateOwnedItemAction,
    null
  )
  const [deleteState, deleteFormAction, isDeletePending] = useActionState(
    deleteOwnedItemAction,
    null
  )

  return (
    <Card>
      <CardHeader className="space-y-2">
        <CardTitle className="flex flex-wrap items-center gap-2 text-lg">
          <span>{item.name}</span>
          <Badge>${item.price.toFixed(2)}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form action={formAction} className="space-y-4" noValidate>
          <input type="hidden" name="itemId" value={item.id} readOnly />
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor={`name-${item.id}`}>Name</FieldLabel>
              <Input
                id={`name-${item.id}`}
                name="name"
                defaultValue={item.name}
              />
            </Field>
            <Field>
              <FieldLabel htmlFor={`description-${item.id}`}>
                Description
              </FieldLabel>
              <Textarea
                id={`description-${item.id}`}
                name="description"
                defaultValue={item.description}
              />
            </Field>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <Field>
                <FieldLabel htmlFor={`price-${item.id}`}>Price</FieldLabel>
                <Input
                  id={`price-${item.id}`}
                  name="price"
                  type="number"
                  step="0.01"
                  defaultValue={item.price}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor={`tax-${item.id}`}>Tax</FieldLabel>
                <Input
                  id={`tax-${item.id}`}
                  name="tax"
                  type="number"
                  step="0.01"
                  defaultValue={item.tax}
                />
              </Field>
            </div>
            <Field>
              <FieldLabel htmlFor={`imageUrl-${item.id}`}>Image URL</FieldLabel>
              <Input
                id={`imageUrl-${item.id}`}
                name="imageUrl"
                defaultValue={item.image_url ?? ''}
              />
            </Field>
          </FieldGroup>

          <ActionFeedback state={state} />

          <Button type="submit" disabled={isPending} className="cursor-pointer">
            {isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </form>

        <form action={deleteFormAction}>
          <input type="hidden" name="itemId" value={item.id} readOnly />
          <ActionFeedback state={deleteState} />
          <Button
            type="submit"
            variant="destructive"
            disabled={isDeletePending}
            className="mt-3 cursor-pointer"
          >
            {isDeletePending ? 'Deleting...' : 'Delete Item'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

export const MePageClient = ({ user, ownedItems }: MePageClientProps) => {
  const [activeTab, setActiveTab] = useState<'profile' | 'items'>('profile')

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

  return (
    <section className="mx-auto w-full max-w-4xl space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">My Account</h1>
        <p className="text-muted-foreground">
          Manage your profile settings and only your own items.
        </p>
      </header>

      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant={activeTab === 'profile' ? 'default' : 'outline'}
          onClick={() => setActiveTab('profile')}
          className="cursor-pointer"
        >
          Profile
        </Button>
        <Button
          type="button"
          variant={activeTab === 'items' ? 'default' : 'outline'}
          onClick={() => setActiveTab('items')}
          className="cursor-pointer"
        >
          My Items ({ownedItems.length})
        </Button>
      </div>

      {activeTab === 'profile' && (
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
                <strong>Role:</strong>{' '}
                {user.is_superuser ? 'Superuser' : 'User'}
              </p>
              <p>
                <strong>Status:</strong>{' '}
                {user.is_active ? 'Active' : 'Inactive'}
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
              <form
                action={passwordFormAction}
                className="space-y-4"
                noValidate
              >
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
                    Type DELETE to confirm
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
      )}

      {activeTab === 'items' && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-2xl font-semibold">My Items</h2>
            <Link
              href="/items/new"
              className="border-primary text-primary hover:bg-primary rounded-md border px-4 py-2 font-semibold transition-colors hover:text-white"
            >
              Create Item
            </Link>
          </div>

          {ownedItems.length === 0 && (
            <Card>
              <CardContent className="space-y-3 py-6">
                <p className="text-muted-foreground">
                  You have not created any items yet.
                </p>
                <Link
                  href="/items/new"
                  className="text-primary inline-block font-semibold underline"
                >
                  Create your first item
                </Link>
              </CardContent>
            </Card>
          )}

          <div className="grid gap-4">
            {ownedItems.map((item) => (
              <OwnedItemEditor key={item.id} item={item} />
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
