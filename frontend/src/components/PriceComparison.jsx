import { useState } from 'react'

function PriceComparison({ car, platforms }) {
  const [prices, setPrices] = useState({})
  const [showTable, setShowTable] = useState(false)

  const handlePriceChange = (platform, value) => {
    setPrices(prev => ({
      ...prev,
      [platform]: value
    }))
  }

  const clearPrices = () => {
    setPrices({})
  }

  const exportToExcel = () => {
    const validPrices = Object.entries(prices).filter(([_, price]) => price && !isNaN(parseFloat(price)))
    if (validPrices.length === 0) {
      alert('请先输入价格数据')
      return
    }

    const dailyPrice = Math.min(...validPrices.map(([_, price]) => parseFloat(price)))
    const weeklyPrice = dailyPrice * 6
    const monthlyPrice = dailyPrice * 22

    const csvContent = [
      ['平台', '日租金(元)', '周租金(元)', '月租金(元)'],
      ...validPrices.map(([platform, price]) => [
        platform,
        price,
        (parseFloat(price) * 6).toFixed(2),
        (parseFloat(price) * 22).toFixed(2)
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `价格对比_${car.model_name}_${new Date().toLocaleDateString()}.csv`
    a.click()
    document.body.removeChild(a)
  }

  const validPrices = Object.entries(prices).filter(([_, price]) => price && !isNaN(parseFloat(price)))
  const minPrice = validPrices.length > 0 
    ? Math.min(...validPrices.map(([_, price]) => parseFloat(price)))
    : null

  const minPricePlatform = validPrices.find(([_, p]) => parseFloat(p) === minPrice)?.[0]

  if (!showTable) {
    return (
      <button
        onClick={() => setShowTable(true)}
        className="text-xs text-emerald-600 hover:text-emerald-700 underline"
      >
        记录价格对比
      </button>
    )
  }

  return (
    <div className="mt-3 p-4 bg-gradient-to-b from-gray-50 to-white rounded-lg shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-gray-700">价格对比表</span>
        <div className="flex items-center gap-2">
          <button
            onClick={clearPrices}
            className="text-xs text-red-500 hover:text-red-600 px-2 py-1 rounded hover:bg-red-50"
          >
            清空
          </button>
          <button
            onClick={exportToExcel}
            className="text-xs text-blue-500 hover:text-blue-600 px-2 py-1 rounded hover:bg-blue-50"
          >
            导出Excel
          </button>
          <button
            onClick={() => setShowTable(false)}
            className="text-xs text-gray-400 hover:text-gray-600"
          >
            收起
          </button>
        </div>
      </div>
      
      <div className="space-y-2">
        {platforms.map(platform => (
          <div key={platform.name} className="flex items-center gap-2">
            <span className="text-xs text-gray-500 w-20">{platform.name}</span>
            <input
              type="number"
              placeholder="日租金"
              value={prices[platform.name] || ''}
              onChange={(e) => handlePriceChange(platform.name, e.target.value)}
              className="flex-1 px-2 py-1.5 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-300"
            />
            <span className="text-xs text-gray-400 w-10">元/天</span>
            {prices[platform.name] && minPrice && parseFloat(prices[platform.name]) === minPrice && (
              <span className="text-xs text-emerald-600 font-medium px-2 py-0.5 bg-emerald-50 rounded">最低</span>
            )}
          </div>
        ))}
      </div>

      {validPrices.length > 0 && (
        <div className="mt-4 p-3 bg-emerald-50 rounded-lg">
          <div className="text-sm font-semibold text-emerald-700 mb-2">价格汇总</div>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-white p-2 rounded shadow-sm">
              <div className="text-xs text-gray-500">日租金</div>
              <div className="text-lg font-bold text-emerald-600">¥{minPrice}</div>
              <div className="text-xs text-gray-400">元/天</div>
            </div>
            <div className="bg-white p-2 rounded shadow-sm">
              <div className="text-xs text-gray-500">周租金</div>
              <div className="text-lg font-bold text-blue-600">¥{(minPrice * 6).toFixed(0)}</div>
              <div className="text-xs text-gray-400">元 (日均¥{(minPrice * 6 / 7).toFixed(0)})</div>
            </div>
            <div className="bg-white p-2 rounded shadow-sm">
              <div className="text-xs text-gray-500">月租金</div>
              <div className="text-lg font-bold text-purple-600">¥{(minPrice * 22).toFixed(0)}</div>
              <div className="text-xs text-gray-400">元 (日均¥{(minPrice * 22 / 30).toFixed(1)})</div>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500 text-center">
            最低价平台: <span className="font-medium text-emerald-600">{minPricePlatform}</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default PriceComparison