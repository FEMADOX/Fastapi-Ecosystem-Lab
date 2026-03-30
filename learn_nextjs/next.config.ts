import path from 'path'
import { NextConfig } from 'next'

const nextConfig: NextConfig = {
  reactCompiler: true,
  logging: {
    fetches: {
      fullUrl: true
    }
  },
  cacheComponents: true,
  env: {
    path: path.resolve(__dirname, '../.env'),
    SECRET_KEY: process.env.SECRET_KEY,
    LEARN_FASTAPI_API_URL: process.env.LEARN_FASTAPI_API_URL,
    ENVIRONMENT: process.env.ENVIRONMENT
  }
}

export default nextConfig
