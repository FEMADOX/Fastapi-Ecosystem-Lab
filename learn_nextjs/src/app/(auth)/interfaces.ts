import { z } from 'zod'
import { ApiProxyResponse } from '../api/interfaces'
import { ApiVersion } from '../api/types'

export interface AuthFormProps {
  title: string
  submitLabel: string
  submittingLabel: string
  schema: z.ZodTypeAny
  actionApi: (
    email: string,
    password: string,
    apiVersion?: ApiVersion
  ) => Promise<ApiProxyResponse<unknown>>
  redirectPath: string
}
