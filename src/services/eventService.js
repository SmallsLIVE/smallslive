import apiClient from './axiosService.js'

const urlBase = `/events/?venue=${3}`

export default {
  getAllEvents() {
    return apiClient.get(`${urlBase}`)
  },
}