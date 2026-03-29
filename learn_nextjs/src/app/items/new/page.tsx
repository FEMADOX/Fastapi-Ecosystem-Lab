'use client'

import { createItem } from '@/app/api/endpoints'
import { FormEvent, useState } from 'react'
import { newItemFormSchema } from './schema'

const ItemNewPage = () => {
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [submitError, setSubmitError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const submitForm = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitError('')
    setFieldErrors({})

    const formData = new FormData(event.currentTarget)
    const rawFormData = Object.fromEntries(formData.entries())
    const parseResult = newItemFormSchema.safeParse(rawFormData)

    if (!parseResult.success) {
      const flattenedErrors = parseResult.error.flatten().fieldErrors
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
        className="
          grid gap-2 gap-y-3 max-w-md grid-cols-[max-content_1fr]
         [&>div>input]:bg-gray-300 [&>div>input]:rounded [&>div>input]:text-black [&>div>input]:px-2 [&>div>input]:w-full
         "
        onSubmit={handleSubmit}
        method="POST"
        noValidate
      >
        {/* User Id should not be visible for non-admin users */}
        {/* <label htmlFor="userId">User ID:</label>
        <div>
          <input type="text" id="userId" name="userId" />
          {fieldErrors.userId != null && (
            <p className="mt-1 text-sm text-red-600">{fieldErrors.userId}</p>
          )}
        </div> */}
        {/* TODO (FENYXZ): Implement the logic to fetch the current user's ID through the authentication context or API */}
        {/* User ID is hidden for non-admin users and the default value is the current user's ID obtained from the authorization */}
        <input type="hidden" id="userId" name="userId" value={''} />

        <label htmlFor="name">Name:</label>
        <div>
          <input type="text" id="name" name="name" required />
          {fieldErrors.name != null && (
            <p className="mt-1 text-sm text-red-600">{fieldErrors.name}</p>
          )}
        </div>

        <label htmlFor="description">Description:</label>
        <div>
          <textarea
            className="bg-gray-300 rounded text-black px-2 w-full"
            id="description"
            name="description"
            required
          />
          {fieldErrors.description != null && (
            <p className="mt-1 text-sm text-red-600">
              {fieldErrors.description}
            </p>
          )}
        </div>

        <label htmlFor="price">Price:</label>
        <div>
          <input
            type="number"
            id="price"
            name="price"
            min={0}
            step="0.01"
            required
          />
          {fieldErrors.price != null && (
            <p className="mt-1 text-sm text-red-600">{fieldErrors.price}</p>
          )}
        </div>

        <label htmlFor="tax">Tax:</label>
        <div>
          <input
            type="number"
            id="tax"
            name="tax"
            min={0}
            step="0.01"
            required
          />
          {fieldErrors.tax != null && (
            <p className="mt-1 text-sm text-red-600">{fieldErrors.tax}</p>
          )}
        </div>

        <label htmlFor="imageUrl">Image URL:</label>
        <div>
          <input type="url" id="imageUrl" name="imageUrl" />
          {fieldErrors.imageUrl != null && (
            <p className="mt-1 text-sm text-red-600">{fieldErrors.imageUrl}</p>
          )}
        </div>

        {submitError.length > 0 && (
          <p className="text-red-600 col-span-2" role="alert">
            {submitError}
          </p>
        )}

        <button
          className="bg-gray-700 col-span-2 mx-auto px-10 rounded-md py-1 text-white [&:hover]:cursor-pointer [&:hover]:bg-gray-800 [&:hover]:text-gray-300 transition-colors"
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
