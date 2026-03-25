import { NextConfig } from 'next'

const nextConfig: NextConfig = {
  reactCompiler: true,
  logging: {
    fetches: {
      fullUrl: true
    }
  },
  cacheComponents: true
}

export default nextConfig
