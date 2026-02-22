import { useState, useEffect } from 'react'

function SearchForm({ onSearch, disabled }) {
  const formatLocalDateTime = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    return `${year}-${month}-${day}T${hours}:${minutes}`
  }

  const getDefaultPickupTime = () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow.setHours(10, 0, 0, 0)
    return formatLocalDateTime(tomorrow)
  }

  const getDefaultReturnTime = () => {
    const day7 = new Date()
    day7.setDate(day7.getDate() + 7)
    day7.setHours(10, 0, 0, 0)
    return formatLocalDateTime(day7)
  }

  const [formData, setFormData] = useState({
    query: '',
    city: '',
    pickupTime: getDefaultPickupTime(),
    returnTime: getDefaultReturnTime(),
  })

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!formData.query || !formData.city || !formData.pickupTime || !formData.returnTime) {
      alert('请填写所有字段')
      return
    }

    const pickup = new Date(formData.pickupTime)
    const returnDate = new Date(formData.returnTime)

    if (returnDate <= pickup) {
      alert('还车时间必须晚于取车时间')
      return
    }

    onSearch(formData)
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-1">
            搜索车型
          </label>
          <input
            type="text"
            id="query"
            name="query"
            value={formData.query}
            onChange={handleChange}
            placeholder="输入品牌、车系或车型，如：比亚迪、Model 3、萤火虫发光版"
            disabled={disabled}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:bg-gray-100 text-base"
            required
          />
          <p className="mt-1 text-xs text-gray-400">
            精确搜索：输入完整车型名（如"萤火虫发光版"） | 模糊搜索：输入品牌或车系（如"firefly"、"Model 3"）
          </p>
        </div>

        <div>
          <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">
            城市
          </label>
          <input
            type="text"
            id="city"
            name="city"
            value={formData.city}
            onChange={handleChange}
            placeholder="例如：北京"
            disabled={disabled}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:bg-gray-100"
            required
          />
        </div>

        <div>{/* 占位，保持布局对齐 */}</div>

        <div>
          <label htmlFor="pickupTime" className="block text-sm font-medium text-gray-700 mb-1">
            取车时间
          </label>
          <input
            type="datetime-local"
            id="pickupTime"
            name="pickupTime"
            value={formData.pickupTime}
            onChange={handleChange}
            disabled={disabled}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:bg-gray-100"
            required
          />
        </div>

        <div>
          <label htmlFor="returnTime" className="block text-sm font-medium text-gray-700 mb-1">
            还车时间
          </label>
          <input
            type="datetime-local"
            id="returnTime"
            name="returnTime"
            value={formData.returnTime}
            onChange={handleChange}
            disabled={disabled}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:bg-gray-100"
            required
          />
        </div>
      </div>

      <div className="mt-6">
        <button
          type="submit"
          disabled={disabled}
          className="w-full bg-emerald-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors text-base"
        >
          {disabled ? '搜索中...' : '搜索价格'}
        </button>
      </div>
    </form>
  )
}

export default SearchForm
