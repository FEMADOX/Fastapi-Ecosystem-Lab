import {
  Button,
  Field,
  FieldGroup,
  FieldLabel,
  Form,
  Input,
  PasswordInput
} from '@/components/ui'
import { ActionFeedback } from './ActionFeedback'
import type { FieldsBaseComponentProps, ProfileUpdateFormProps } from './types'
import { emailFields, passwordFields } from './utils'

const FieldsBaseComponent = ({ fields }: FieldsBaseComponentProps) => (
  <FieldGroup>
    {fields.map((field) => (
      <Field key={field.inputId}>
        <FieldLabel htmlFor={field.inputId}>{field.label}</FieldLabel>
        {field.inputType === 'password' ? (
          <PasswordInput
            id={field.inputId}
            name={field.inputName}
            defaultValue={field.defaultValue}
          />
        ) : (
          <Input
            id={field.inputId}
            name={field.inputName}
            type={field.inputType}
            defaultValue={field.defaultValue}
          />
        )}
      </Field>
    ))}
  </FieldGroup>
)

const ProfileUpdateForm = ({
  action,
  state,
  isPending,
  submitLabel,
  pendingLabel,
  submitVariant = 'default',
  formVariant,
  userEmail,
  children
}: ProfileUpdateFormProps) => {
  return (
    <Form action={action} noValidate>
      {formVariant === 'email' && userEmail ? (
        <FieldsBaseComponent fields={emailFields(userEmail)} />
      ) : formVariant === 'password' ? (
        <FieldsBaseComponent fields={passwordFields()} />
      ) : (
        children
      )}

      <ActionFeedback state={state} />

      <Button
        type="submit"
        variant={submitVariant}
        disabled={isPending}
        className="cursor-pointer"
      >
        {isPending ? pendingLabel : submitLabel}
      </Button>
    </Form>
  )
}

export default ProfileUpdateForm
