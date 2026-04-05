'use client'

import { FormEvent, useActionState, useState } from 'react'
import { z } from 'zod'
import { createItemAction } from '@/actions/items/actions'
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel
} from '@/components/ui/field'
import { NewItemFormProps } from '@/types/items/types'
import { Input } from '@/components/ui/input'
import { clientItemSchema } from '@/schemas/items/new/forms'
import { Textarea } from '@/components/ui/textarea'

export const NewItemForm = ({ userId }: NewItemFormProps) => {
  const [state, formAction, isPending] = useActionState(createItemAction, null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFieldErrors({})

    const formData = new FormData(event.currentTarget)
    const rawFormData = Object.fromEntries(formData.entries())
    const parseResult = clientItemSchema.safeParse(rawFormData)

    if (!parseResult.success) {
      const flattenedErrors = z.flattenError(parseResult.error).fieldErrors
      const nextFieldErrors = Object.fromEntries(
        Object.entries(flattenedErrors)
          .filter(
            ([, messages]) => Array.isArray(messages) && messages.length > 0
          )
          .map(([fieldName, messages]) => [
            fieldName,
            messages[0] ?? 'Invalid value'
          ])
      )
      setFieldErrors(nextFieldErrors)
      return
    }

    formAction(formData)
  }

  return (
    <form
      className={`
        grid gap-y-5 max-w-xl grid-cols-1 md:mx-auto
        [&>div>input]:bg-gray-300 [&>div>input]:rounded [&>div>input]:text-black [&>div>input]:px-2 [&>div>input]:w-full
      `}
      onSubmit={handleSubmit}
      method="POST"
      noValidate
    >
      <FieldGroup className="grid grid-cols-1">
        <Field hidden={true}>
          <Input
            type="hidden"
            id="userId"
            name="userId"
            value={userId}
            readOnly
          />
        </Field>

        <Field data-invalid={!!fieldErrors.name}>
          <FieldLabel htmlFor="name" className="font-semibold">
            Name<span className="text-destructive">*</span>
          </FieldLabel>
          <Input id="name" name="name" type="text" required />
          <FieldError>{fieldErrors.name}</FieldError>
        </Field>

        <Field data-invalid={!!fieldErrors.description}>
          <FieldLabel htmlFor="description" className="font-semibold">
            Description
          </FieldLabel>
          <FieldDescription>A brief description of the item.</FieldDescription>
          <Textarea id="description" name="description" />
          <FieldError>{fieldErrors.description}</FieldError>
        </Field>

        <FieldGroup className="grid grid-cols-[repeat(auto-fit,minmax(50px,100px))]">
          <Field data-invalid={!!fieldErrors.price}>
            <FieldLabel htmlFor="price" className="font-semibold">
              Price
            </FieldLabel>
            <Input
              id="price"
              name="price"
              type="number"
              defaultValue={0.0}
              step="0.01"
              required
            />
            <FieldError>{fieldErrors.price}</FieldError>
          </Field>
          <Field data-invalid={!!fieldErrors.tax}>
            <FieldLabel htmlFor="tax" className="font-semibold">
              Tax
            </FieldLabel>
            <Input
              id="tax"
              name="tax"
              type="number"
              defaultValue={0.0}
              step="0.01"
              required
            />
            <FieldError>{fieldErrors.tax}</FieldError>
          </Field>
        </FieldGroup>

        <Field data-invalid={!!fieldErrors.imageUrl}>
          <FieldLabel htmlFor="imageUrl" className="font-semibold">
            Image URL
          </FieldLabel>
          <FieldDescription>
            A URL pointing to an image of the item.
          </FieldDescription>
          <Input id="imageUrl" name="imageUrl" type="text" />
          <FieldError>{fieldErrors.imageUrl}</FieldError>
        </Field>
      </FieldGroup>

      {state?.error && (
        <p className="text-red-600 col-span-2" role="alert">
          {state.error}
        </p>
      )}

      <button
        className={`
          bg-gray-700 col-span-2 mx-auto px-10 rounded-md py-1 text-white
          [&:hover]:cursor-pointer [&:hover]:bg-gray-800 [&:hover]:text-gray-300 transition-colors
        `}
        type="submit"
        disabled={isPending}
      >
        {isPending ? 'Creating...' : 'Create Item'}
      </button>
    </form>
  )
}
