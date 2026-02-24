import apiClient from './axiosService.js'

const urlBase = `/jazz-photos/`

export default {
  getAllJazzPhotos({ limit, offset }) {
    return apiClient.get(urlBase, {
      params: {
        limit,
        offset
      }
    })
  },
}