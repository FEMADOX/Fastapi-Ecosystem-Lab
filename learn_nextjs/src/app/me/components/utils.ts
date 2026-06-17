import type { FieldsProps } from './types'

export const emailFields = (userEmail: string): FieldsProps => [
  {
    label: 'New Email',
    inputId: 'profileEmail',
    inputName: 'email',
    inputType: 'email',
    defaultValue: userEmail
  },
  {
    label: 'Current Password',
    inputId: 'profileCurrentPasswordForEmail',
    inputName: 'currentPassword',
    inputType: 'password'
  }
]

export const passwordFields = (): FieldsProps => [
  {
    label: 'Current Password',
    inputId: 'profileCurrentPasswordForPassword',
    inputName: 'currentPassword',
    inputType: 'password'
  },
  {
    label: 'New Password',
    inputId: 'profileNewPassword',
    inputName: 'newPassword',
    inputType: 'password'
  },
  {
    label: 'Confirm New Password',
    inputId: 'profileConfirmPassword',
    inputName: 'confirmPassword',
    inputType: 'password'
  }
]
