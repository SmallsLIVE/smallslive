import axios from 'axios'

const ApiClient = () => {
  const defaultOptions = {
    baseURL: import.meta.env.VITE_API_URL,
    headers: { Accept: 'application/json' }
  }

  const instance = axios.create(defaultOptions)

  instance.interceptors.request.use(async (request) => {


    const contentType = request.contentType
    if (contentType) {
      request.headers['Content-Type'] = contentType
    } else {
      request.headers['Content-Type'] = 'application/json'
    }

    return request
  })

  return instance
}

export default ApiClient()