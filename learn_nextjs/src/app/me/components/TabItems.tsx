import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useActionState, useEffect } from 'react'
import {
  deleteOwnedItemAction,
  updateOwnedItemAction
} from '@/actions/user/actions'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
// import { ActionFeedback } from '../ActionFeedback'
import type { OwnedItemEditorProps, TabItemProps } from './types'

const OwnedItemEditor = ({ item }: OwnedItemEditorProps) => {
  const router = useRouter()
  const [updateState, updateFormAction, isUpdatePending] = useActionState(
    updateOwnedItemAction,
    null
  )
  const [deleteState, deleteFormAction, isDeletePending] = useActionState(
    deleteOwnedItemAction,
    null
  )

  useEffect(() => {
    if (updateState === null && deleteState === null) return
    router.refresh()
  }, [updateState, deleteState, router])

  return (
    <Card>
      <CardHeader className="space-y-2">
        <CardTitle className="flex flex-wrap items-center gap-2 text-lg">
          <span>{item.name}</span>
          <Badge>${item.price.toFixed(2)}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form action={updateFormAction} className="space-y-4" noValidate>
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

          <Button
            type="submit"
            disabled={isUpdatePending}
            className="cursor-pointer"
          >
            {isUpdatePending ? 'Saving...' : 'Save Changes'}
          </Button>
        </form>

        <form action={deleteFormAction}>
          <input type="hidden" name="itemId" value={item.id} readOnly />
          <Button
            type="submit"
            variant="destructive"
            disabled={isDeletePending}
            className="cursor-pointer"
          >
            {isDeletePending ? 'Deleting...' : 'Delete Item'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

export const TabItemsComponent = ({ ownedItems, isActive }: TabItemProps) => {
  if (!isActive) return null

  return (
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
  )
}
