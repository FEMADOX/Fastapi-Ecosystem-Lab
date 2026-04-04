'use client'

import { createItem } from '@/app/api/endpoints'
import { useAuth } from '@/app/hooks/useAuth'
import { FormEvent, useState } from 'react'
import { z } from 'zod'
import { newItemFormSchema } from './schema'
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel
} from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'

const ItemNewPage = () => {
  const { state } = useAuth()

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [submitError, setSubmitError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (state.status !== 'authenticated') return

  const { user } = state

  const submitForm = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitError('')
    setFieldErrors({})

    const formData = new FormData(event.currentTarget)
    const rawFormData = Object.fromEntries(formData.entries())
    const parseResult = newItemFormSchema.safeParse(rawFormData)

    if (!parseResult.success) {
      const flattenedErrors = z.flattenError(parseResult.error).fieldErrors
      const nextFieldErrors = Object.fromEntries(
        Object.entries(flattenedErrors)
          .filter(
            ([, messages]) => Array.isArray(messages) && messages.length > 0
          )
          .map(([fieldName, messages]) => [
            fieldName,
            (messages as string[])[0] ?? 'Invalid value'
          ])
      )

      setFieldErrors(nextFieldErrors)
      return
    }

    setIsSubmitting(true)

    const item = parseResult.data

    await createItem(item)
    event.currentTarget.reset()
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    submitForm(event)
      .catch((error) => {
        console.error('Error creating item:', error)
        setSubmitError('Unable to create item. Please try again.')
      })
      .finally(() => {
        setIsSubmitting(false)
      })
  }

  return (
    <>
      <h1 className="text-3xl mb-8 font-bold">New Item</h1>
      <form
        className={`
          grid gap-y-5 max-w-xl grid-cols-1 md:mx-auto
         [&>div>input]:bg-gray-300 [&>div>input]:rounded [&>div>input]:text-black [&>div>input]:px-2 [&>div>input]:w-full
        `}
        onSubmit={handleSubmit}
        method="POST"
        noValidate
      >
        {/* User Id should not be visible for non-admin users */}
        {/* Implementing FieldGroup and Fields components from shadcn */}
        <FieldGroup className='grid grid-cols-1'>
          <Field hidden={true}>
            <Input
              type="hidden"
              id="userId"
              name="userId"
              value={user.id}
              readOnly
            />
          </Field>

          <Field data-invalid={!!fieldErrors.name}>
            <FieldLabel htmlFor="name" className='font-semibold'>
              Name<span className="text-destructive">*</span>
            </FieldLabel>
            <Input id="name" name="name" type="text" required />
            <FieldError>{fieldErrors.name}</FieldError>
          </Field>

          <Field data-invalid={!!fieldErrors.description}>
            <FieldLabel htmlFor="description" className='font-semibold'>Description</FieldLabel>
            <FieldDescription>
              A brief description of the item.
            </FieldDescription>
            <Textarea id="description" name="description" />
            <FieldError>{fieldErrors.description}</FieldError>
          </Field>

          <FieldGroup className="grid grid-cols-[repeat(auto-fit,minmax(50px,100px))]">
            <Field data-invalid={!!fieldErrors.price}>
              <FieldLabel htmlFor="price" className='font-semibold'>Price</FieldLabel>
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
              <FieldLabel htmlFor="tax" className='font-semibold'>Tax</FieldLabel>
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
            <FieldLabel htmlFor="imageUrl" className='font-semibold'>Image URL</FieldLabel>
            <FieldDescription>
              A URL pointing to an image of the item.
            </FieldDescription>
            <Input id="imageUrl" name="imageUrl" type="text" required />
            <FieldError>{fieldErrors.imageUrl}</FieldError>
          </Field>
        </FieldGroup>

        {submitError.length > 0 && (
          <p className="text-red-600 col-span-2" role="alert">
            {submitError}
          </p>
        )}

        <button
          className={`
          bg-gray-700 col-span-2 mx-auto px-10 rounded-md py-1 text-white
            [&:hover]:cursor-pointer [&:hover]:bg-gray-800 [&:hover]:text-gray-300 transition-colors
          `}
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating...' : 'Create Item'}
        </button>
      </form>
    </>
  )
}

export default ItemNewPage
