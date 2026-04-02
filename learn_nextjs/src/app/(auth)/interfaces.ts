import { ApiProxyResponse } from '../api/interfaces'
import { z } from 'zod'

export interface AuthFormProps {
  title: string
  submitLabel: string
  submittingLabel: string
  schema: z.ZodTypeAny
  actionApi: (
    email: string,
    password: string
  ) => Promise<ApiProxyResponse<unknown>>
  redirectPath: string
}
