'use client'

import { useActionState, useState } from 'react'

import { createItemAction } from '@/actions/items/actions'
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel
} from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import type { NewItemFormProps } from '@/types/items/types'
import type { FormSubmitEvent } from './types'
import { validateItemForm } from './utils'

export const NewItemForm = ({ userId }: NewItemFormProps) => {
  const [state, formAction, isPending] = useActionState(createItemAction, null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  const handleSubmit = (event: FormSubmitEvent) => {
    const { success, flattenedErrors } = validateItemForm(
      event.currentTarget,
      setFieldErrors
    )

    if (!success) {
      event.preventDefault()
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
    }
  }

  return (
    <form
      className={`
        grid max-w-xl grid-cols-1 gap-y-5 md:mx-auto
        [&>div>input]:w-full [&>div>input]:rounded [&>div>input]:bg-gray-300 [&>div>input]:px-2 [&>div>input]:text-black
      `}
      action={formAction}
      onSubmit={handleSubmit}
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
          <Textarea
            id="description"
            name="description"
            defaultValue="No description provided"
          ></Textarea>
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
        <p className="col-span-2 text-red-600" role="alert">
          {state.error}
        </p>
      )}

      <button
        className={`col-span-2 mx-auto rounded-md bg-gray-700 px-10 py-1 text-white transition-colors [&:hover]:cursor-pointer [&:hover]:bg-gray-800 [&:hover]:text-gray-300`}
        type="submit"
        disabled={isPending}
      >
        {isPending ? 'Creating...' : 'Create Item'}
      </button>
    </form>
  )
}
