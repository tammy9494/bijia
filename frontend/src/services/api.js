import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const searchRentalPrices = async (searchParams) => {
  const { query, city, pickupTime, returnTime } = searchParams

  const response = await api.post('/rental/search', {
    query: query,
    city: city,
    pickup_time: pickupTime,
    return_time: returnTime,
  })

  return response.data
}
