import type { SubmitEvent } from 'react'
export type FormSubmitEvent = SubmitEvent<HTMLFormElement>
export type SetFieldErrorsItemForm = React.Dispatch<
  React.SetStateAction<Record<string, string>>
>
