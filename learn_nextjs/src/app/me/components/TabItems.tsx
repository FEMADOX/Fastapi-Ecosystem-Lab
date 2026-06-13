import { Camera } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { type ChangeEvent, useActionState, useEffect, useRef } from 'react'
import {
  deleteOwnedItemAction,
  updateOwnedItemAction,
  updateOwnedItemImageAction
} from '@/actions/user/actions'
import { ProductImage } from '@/components/product-image'
import {
  AspectRatio,
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  DeleteIcon,
  type DeleteIconHandle,
  Field,
  FieldGroup,
  FieldLabel,
  Form,
  Input,
  Textarea
} from '@/components/ui'
import type { OwnedItemEditorProps, TabItemProps } from './types'

const OwnedItemEditor = ({ item }: OwnedItemEditorProps) => {
  const router = useRouter()
  const deleteIconRef = useRef<DeleteIconHandle>(null)
  const imageFormRef = useRef<HTMLFormElement>(null)
  const [updateState, updateFormAction, isUpdatePending] = useActionState(
    updateOwnedItemAction,
    null
  )
  const [imageState, imageFormAction, isImagePending] = useActionState(
    updateOwnedItemImageAction,
    null
  )
  const [deleteState, deleteFormAction, isDeletePending] = useActionState(
    deleteOwnedItemAction,
    null
  )

  useEffect(() => {
    if (updateState === null && imageState === null && deleteState === null)
      return
    router.refresh()
  }, [updateState, imageState, deleteState, router])

  const submitImageUpdate = (event: ChangeEvent<HTMLInputElement>) => {
    if (!event.currentTarget.files?.length) return
    imageFormRef.current?.requestSubmit()
  }

  return (
    <Card className="max-w-md min-w-75 w-[90%]">
      <CardHeader className="grid grid-rows-[1fr_auto] items-center">
        <Form ref={imageFormRef} action={imageFormAction}>
          <Input type="hidden" name="itemId" value={item.id} readOnly />
          <AspectRatio
            ratio={1.268115942}
            className="group relative overflow-hidden flex rounded"
          >
            <FieldLabel
              htmlFor={`image-file-${item.id}`}
              className="block size-full cursor-pointer"
              aria-label={`Update image for ${item.name}`}
            >
              <ProductImage
                src={item.image_url}
                alt={item.description}
                className="block size-full object-cover object-center transition-opacity group-hover:opacity-75"
                width={500}
                height={500}
                loading="eager"
              />
              <span className="absolute inset-0 grid place-items-center bg-black/0 opacity-0 transition-all group-hover:bg-black/30 group-hover:opacity-100">
                <span className="rounded-full bg-background p-3 text-foreground shadow-sm">
                  <Camera className="size-5 hover:" aria-hidden="true" />
                </span>
              </span>
            </FieldLabel>
            <Input
              id={`image-file-${item.id}`}
              name="image_file"
              type="file"
              accept="image/*"
              className="sr-only"
              disabled={isImagePending}
              onChange={submitImageUpdate}
            />
          </AspectRatio>
        </Form>
        <div className="mt-4 flex w-full justify-between">
          <CardTitle className="flex flex-wrap items-center gap-2 text-lg">
            <span>{item.name}</span>
            <Badge>${item.price.toFixed(2)}</Badge>
          </CardTitle>
          <Form action={deleteFormAction}>
            <Input type="hidden" name="itemId" value={item.id} readOnly />
            <Button
              type="submit"
              variant="destructive"
              disabled={isDeletePending}
              className="cursor-pointer"
              onMouseEnter={() => deleteIconRef.current?.startAnimation()}
              onMouseLeave={() => deleteIconRef.current?.stopAnimation()}
            >
              <DeleteIcon ref={deleteIconRef} />
            </Button>
          </Form>
        </div>
      </CardHeader>
      <CardContent>
        <Form action={updateFormAction} className="items-center" noValidate>
          <Input type="hidden" name="itemId" value={item.id} readOnly />
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
          </FieldGroup>

          <Button
            type="submit"
            disabled={isUpdatePending}
            className="cursor-pointer text-lg hover:bg-primary/70 transition-colors"
          >
            {isUpdatePending ? 'Saving...' : 'Save Changes'}
          </Button>
        </Form>
      </CardContent>
    </Card>
  )
}

export const TabItemsComponent = ({ ownedItems, isActive }: TabItemProps) => {
  if (!isActive) return null

  return (
    <div className="flex flex-col gap-6">
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

      <div className="grid grid-cols-[repeat(auto-fill,minmax(300px,1fr))] justify-items-center gap-4 md:gap-8">
        {ownedItems.map((item) => (
          <OwnedItemEditor key={item.id} item={item} />
        ))}
      </div>
    </div>
  )
}
