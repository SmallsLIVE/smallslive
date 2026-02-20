import apiClient from './axiosService.js'

const urlBase = `/events/`

export default {
  getAllEvents({ venue=3, limit, offset }) {
    return apiClient.get(urlBase, {
      params: {
        venue,
        limit,
        offset
      }
    })
  },
}