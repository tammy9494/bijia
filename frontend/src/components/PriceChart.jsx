import { useState, useEffect } from 'react'

function PriceChart({ carName, platforms }) {
  const [priceHistory, setPriceHistory] = useState(() => {
    const saved = localStorage.getItem(`price_history_${carName}`)
    return saved ? JSON.parse(saved) : []
  })
  const [showChart, setShowChart] = useState(false)
  const [newPrice, setNewPrice] = useState({})
  const [selectedPlatform, setSelectedPlatform] = useState('')

  useEffect(() => {
    localStorage.setItem(`price_history_${carName}`, JSON.stringify(priceHistory))
  }, [priceHistory, carName])

  const addPriceRecord = () => {
    if (!selectedPlatform || !newPrice[selectedPlatform]) return

    const record = {
      id: Date.now().toString(),
      date: new Date().toLocaleDateString('zh-CN'),
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
      platform: selectedPlatform,
      price: parseFloat(newPrice[selectedPlatform]),
      carName: carName
    }

    setPriceHistory(prev => [...prev, record].slice(-50))
    setNewPrice(prev => ({ ...prev, [selectedPlatform]: '' }))
    
    if (priceHistory.length > 0) {
      const lastRecord = priceHistory.filter(r => r.platform === selectedPlatform).slice(-1)[0]
      if (lastRecord) {
        const priceChange = parseFloat(newPrice[selectedPlatform]) - lastRecord.price
        if (Math.abs(priceChange) > 0) {
          alert(`价格变动提醒：${selectedPlatform}的价格从¥${lastRecord.price}变为¥${newPrice[selectedPlatform]}，${priceChange > 0 ? '上涨' : '下降'}¥${Math.abs(priceChange).toFixed(0)}`)
        }
      }
    }
  }

  const clearHistory = () => {
    if (confirm('确定要清空所有历史记录吗？')) {
      setPriceHistory([])
      localStorage.removeItem(`price_history_${carName}`)
    }
  }

  const getPlatformPrices = (platform) => {
    return priceHistory
      .filter(r => r.platform === platform)
      .slice(-10)
      .sort((a, b) => new Date(a.date + ' ' + a.time) - new Date(b.date + ' ' + b.time))
  }

  const getAllPrices = () => {
    return priceHistory
      .slice(-20)
      .sort((a, b) => new Date(a.date + ' ' + a.time) - new Date(b.date + ' ' + b.time))
  }

  const maxPrice = Math.max(...priceHistory.map(r => r.price), 1)
  const minPrice = Math.min(...priceHistory.map(r => r.price), maxPrice)
  const priceRange = maxPrice - minPrice || 1

  if (!showChart) {
    return (
      <button
        onClick={() => setShowChart(true)}
        className="text-xs text-emerald-600 hover:text-emerald-700 underline ml-2"
      >
        价格走势
      </button>
    )
  }

  const allPrices = getAllPrices()
  const platformColors = {
    '一嗨租车': '#10b981',
    '神州租车': '#3b82f6',
    '悟空租车': '#8b5cf6',
    '携程租车': '#f59e0b'
  }

  return (
    <div className="mt-3 p-4 bg-gradient-to-b from-blue-50 to-white rounded-lg shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-gray-700">价格历史记录</span>
        <div className="flex items-center gap-2">
          <button
            onClick={clearHistory}
            className="text-xs text-red-500 hover:text-red-600 px-2 py-1 rounded hover:bg-red-50"
          >
            清空
          </button>
          <button
            onClick={() => setShowChart(false)}
            className="text-xs text-gray-400 hover:text-gray-600"
          >
            收起
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-3">
        <select
          value={selectedPlatform}
          onChange={(e) => setSelectedPlatform(e.target.value)}
          className="flex-1 px-2 py-1.5 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">选择平台</option>
          {platforms.map(p => (
            <option key={p.name} value={p.name}>{p.name}</option>
          ))}
        </select>
        <input
          type="number"
          placeholder="日租金"
          value={newPrice[selectedPlatform] || ''}
          onChange={(e) => setNewPrice(prev => ({ ...prev, [selectedPlatform]: e.target.value }))}
          className="w-20 px-2 py-1.5 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <span className="text-xs text-gray-400">元/天</span>
        <button
          onClick={addPriceRecord}
          disabled={!selectedPlatform || !newPrice[selectedPlatform]}
          className="px-3 py-1.5 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          记录
        </button>
      </div>

      {allPrices.length > 0 ? (
        <div className="space-y-4">
          <div className="text-xs text-gray-500 mb-2">价格走势图（最近{allPrices.length}条记录）</div>
          
          <div className="relative h-32 bg-gray-100 rounded-lg p-2">
            <div className="absolute inset-0 flex items-end gap-1 px-2">
              {allPrices.map((record, index) => {
                const height = ((record.price - minPrice) / priceRange) * 100
                const color = platformColors[record.platform] || '#6b7280'
                return (
                  <div
                    key={record.id}
                    className="flex flex-col items-center group"
                    title={`${record.date} ${record.time}\n${record.platform}: ¥${record.price}/天`}
                  >
                    <div
                      className="w-5 rounded-t transition-all hover:opacity-80"
                      style={{ 
                        height: `${Math.max(height, 10)}%`, 
                        backgroundColor: color,
                        minHeight: '8px'
                      }}
                    />
                  </div>
                )
              })}
            </div>
          </div>

          <div className="flex items-center justify-center gap-4 text-xs">
            {Object.entries(platformColors).map(([name, color]) => (
              <div key={name} className="flex items-center gap-1">
                <span className="w-3 h-3 rounded" style={{ backgroundColor: color }} />
                <span className="text-gray-500">{name}</span>
              </div>
            ))}
          </div>

          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="text-xs text-gray-500 mb-2">最近记录</div>
            <div className="max-h-32 overflow-y-auto space-y-1">
              {allPrices.slice(-10).reverse().map((record) => (
                <div key={record.id} className="flex items-center justify-between text-xs py-1 px-2 bg-gray-50 rounded">
                  <div className="flex items-center gap-2">
                    <span 
                      className="w-2 h-2 rounded-full" 
                      style={{ backgroundColor: platformColors[record.platform] || '#6b7280' }} 
                    />
                    <span className="text-gray-400">{record.date} {record.time}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-600">{record.platform}</span>
                    <span className="font-medium text-blue-600">¥{record.price}/天</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-xs text-gray-400 text-center py-6">
          暂无价格记录，请先记录各平台价格
        </div>
      )}
    </div>
  )
}

export default PriceChart