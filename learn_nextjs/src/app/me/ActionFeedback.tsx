import type { ActionFeedbackProps } from './types'

export const ActionFeedback = ({ state }: ActionFeedbackProps) => {
  if (!state) return null

  return (
    <p
      className={`text-sm ${state.error ? 'text-destructive' : 'text-green-700'}`}
      role="status"
      aria-live="polite"
    >
      {state.error ?? state.success}
    </p>
  )
}
