import type { NextApiRequest, NextApiResponse } from 'next'
import httpProxy from 'http-proxy'
import { API_BASE_URL } from '@/common/const'
import Cookies from 'cookies'
import { IncomingMessage, ServerResponse } from 'http'

const target = API_BASE_URL
const proxy = httpProxy.createProxyServer({
  target,
  changeOrigin: true,
  ignorePath: true
})

export const config = {
  api: {
    bodyParser: false,
    externalResolver: true
  }
}

export default (req: NextApiRequest, res: NextApiResponse) => {
  // Return a Promise to let Next.js know when we're done
  // processing the request:
  return new Promise<void>((resolve, reject) => {
    // In case the current API request is for logging in,
    // we'll need to intercept the API response.
    // More on that in a bit.
    const rawUrl = req.url ?? ''
    const pathname = new URL(rawUrl, `http://${req.headers.host ?? 'localhost'}`).pathname
    const isLogin = pathname === '/api/latest/token'

    // Get the `auth-token` cookie:
    const cookies = new Cookies(req, res)
    const authToken = cookies.get('auth-token')

    // Rewrite the URL: strip out the leading '/api/latest'.
    // For example, '/api/latest/token' would become '/token'.
    // ️You might want to adjust this depending
    // on the base path of your API.
    req.url = rawUrl.replace(/^\/api\/latest/, '')

    // Don't forward cookies to the API:
    req.headers.cookie = ''

    // Set auth-token header from cookie:
    if (authToken) {
      req.headers['auth-token'] = authToken
    }

    // In case the request is for login, we need to
    // intercept the API's response. It contains the
    // auth token that we want to strip out and set
    // as an HTTP-only cookie.
    if (isLogin) {
      proxy.once('proxyRes', (_proxyRes, _req, _res) => {
        interceptLoginResponse(_proxyRes, _req, _res, res)
      })
    }

    const toError = (value: unknown): Error => {
      return value instanceof Error ? value : new Error(String(value))
    }

    // Don't forget to handle errors:
    proxy.once('error', (err) => reject(toError(err)))

    // Forward the request to the API
    proxy.web(req, res, {
      target,

      // Don't autoRewrite because we manually rewrite
      // the URL in the route handler.
      autoRewrite: false,

      // In case we're dealing with a login request,
      // we need to tell http-proxy that we'll handle
      // the client-response ourselves (since we don't
      // want to pass along the auth token).
      selfHandleResponse: isLogin
    })

    const isRecord = (value: unknown): value is Record<string, unknown> => {
      return typeof value === 'object' && value !== null
    }

    function interceptLoginResponse (proxyRes: IncomingMessage, _req: IncomingMessage, _res: ServerResponse, nextRes: NextApiResponse): void {
      // Read the API's response body from
      // the stream:
      let apiResponseBody = ''
      proxyRes.on('data', (chunk: string) => {
        apiResponseBody += chunk
      })

      proxyRes.on('data', (chunk: string) => {
        apiResponseBody += chunk
      })

      // Once we've read the entire API
      // response body, we're ready to
      // handle it:
      proxyRes.on('end', () => {
        try {
          const parsed: unknown = JSON.parse(apiResponseBody)

          if (!isRecord(parsed) || typeof parsed.authToken !== 'string') {
            reject(new Error('Invalid API response'))
            return
          }

          // Extract the authToken from API's response:
          const authToken = parsed.authToken

          // Set the authToken as an HTTP-only cookie.
          // We'll also set the SameSite attribute to
          // 'lax' for some additional CSRF protection.
          const cookies = new Cookies(_req, _res)
          cookies.set('auth-token', authToken, {
            httpOnly: true,
            sameSite: 'lax'
          })

          // Our response to the client won't contain
          // the actual authToken. This way the auth token
          // never gets exposed to the client.
          nextRes.status(200).json({ loggedIn: true })
          resolve()
        } catch (err) {
          reject(toError(err))
        }
      })
    }
  })
}

// export const handler = async (req: NextApiRequest, res: NextApiResponse): Promise<void> => {
//   const queryIndex = req.url?.indexOf('?') ?? -1
//   const query = queryIndex >= 0 && req.url ? req.url.slice(queryIndex) : ''
//   const path = Array.isArray(req.query.path) ? req.query.path.join('/') : ''

//   // Rewrite /api/* to target/* while preserving query string.
//   req.url = `/${path}${query}`

//   try {
//     await new Promise<void>((resolve, reject) => {
//       proxy.web(req, res, undefined, (error) => {
//         reject(error instanceof Error ? error : new Error('Proxy request failed'))
//       })

//       res.on('close', () => {
//         resolve()
//       })
//     })
//   } catch (error) {
//     if (!res.headersSent) {
//       res.status(502).json({
//         message: 'Bad Gateway',
//         detail: error instanceof Error ? error.message : 'Unknown proxy error'
//       })
//     }
//   }
// }

// export default handler
