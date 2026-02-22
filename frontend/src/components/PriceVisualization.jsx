import { useState, useMemo } from 'react'

function PriceVisualization({ results }) {
  const [activeTab, setActiveTab] = useState('comparison')

  const platformColors = {
    '一嗨租车': '#10b981',
    '神州租车': '#3b82f6',
    '悟空租车': '#8b5cf6',
    '携程租车': '#f59e0b'
  }

  const chartData = useMemo(() => {
    if (!results || results.length === 0) return null

    const availableCars = results.filter(r => r.available !== false)
    
    const brandStats = {}
    availableCars.forEach(car => {
      if (!brandStats[car.brand]) {
        brandStats[car.brand] = { count: 0, totalRange: 0, cars: [] }
      }
      brandStats[car.brand].count++
      brandStats[car.brand].totalRange += car.range_km || 0
      brandStats[car.brand].cars.push(car)
    })

    const energyStats = {}
    availableCars.forEach(car => {
      const type = car.energy_type || '纯电动'
      if (!energyStats[type]) {
        energyStats[type] = 0
      }
      energyStats[type]++
    })

    const seatStats = {}
    availableCars.forEach(car => {
      const seats = car.seats || 5
      if (!seatStats[seats]) {
        seatStats[seats] = 0
      }
      seatStats[seats]++
    })

    return {
      totalCars: availableCars.length,
      brandStats,
      energyStats,
      seatStats,
      brands: Object.keys(brandStats).sort((a, b) => brandStats[b].count - brandStats[a].count)
    }
  }, [results])

  if (!chartData || chartData.totalCars === 0) {
    return null
  }

  const maxBrandCount = Math.max(...Object.values(chartData.brandStats).map(b => b.count))
  const maxEnergyCount = Math.max(...Object.values(chartData.energyStats))
  const maxSeatCount = Math.max(...Object.values(chartData.seatStats))

  const energyColors = {
    '纯电动': 'bg-green-500',
    '插电混动': 'bg-blue-500',
    '增程式': 'bg-purple-500'
  }

  return (
    <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="flex border-b border-gray-100">
        <button
          onClick={() => setActiveTab('comparison')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'comparison'
              ? 'text-emerald-600 bg-emerald-50 border-b-2 border-emerald-500'
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          }`}
        >
          品牌分布
        </button>
        <button
          onClick={() => setActiveTab('energy')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'energy'
              ? 'text-emerald-600 bg-emerald-50 border-b-2 border-emerald-500'
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          }`}
        >
          能源类型
        </button>
        <button
          onClick={() => setActiveTab('seats')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'seats'
              ? 'text-emerald-600 bg-emerald-50 border-b-2 border-emerald-500'
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          }`}
        >
          座位分布
        </button>
        <button
          onClick={() => setActiveTab('summary')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'summary'
              ? 'text-emerald-600 bg-emerald-50 border-b-2 border-emerald-500'
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          }`}
        >
          数据摘要
        </button>
      </div>

      <div className="p-4">
        {activeTab === 'comparison' && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-4">品牌车型分布</h3>
            <div className="space-y-3">
              {chartData.brands.slice(0, 8).map(brand => {
                const stat = chartData.brandStats[brand]
                const percentage = (stat.count / chartData.totalCars * 100).toFixed(1)
                const barWidth = (stat.count / maxBrandCount * 100)
                
                return (
                  <div key={brand} className="group">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-600">{brand}</span>
                      <span className="text-xs text-gray-400">{stat.count} 款 ({percentage}%)</span>
                    </div>
                    <div className="h-6 bg-gray-100 rounded-lg overflow-hidden relative">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-lg transition-all duration-300 group-hover:from-emerald-500 group-hover:to-emerald-600"
                        style={{ width: `${barWidth}%` }}
                      />
                      <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-medium text-gray-600">
                        {stat.count}
                      </span>
                    </div>
                    {stat.cars.length > 0 && (
                      <div className="mt-1 text-xs text-gray-400 truncate">
                        {stat.cars.slice(0, 3).map(c => c.model_name).join('、')}
                        {stat.cars.length > 3 && ` 等${stat.cars.length}款`}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {activeTab === 'energy' && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-4">能源类型分布</h3>
            <div className="flex items-center justify-center gap-8">
              <div className="relative w-40 h-40">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                  {(() => {
                    let currentAngle = 0
                    const total = Object.values(chartData.energyStats).reduce((a, b) => a + b, 0)
                    return Object.entries(chartData.energyStats).map(([type, count]) => {
                      const percentage = count / total
                      const angle = percentage * 360
                      const largeArc = angle > 180 ? 1 : 0
                      const endAngle = currentAngle + angle
                      
                      const startRad = (currentAngle * Math.PI) / 180
                      const endRad = (endAngle * Math.PI) / 180
                      
                      const x1 = 50 + 40 * Math.cos(startRad)
                      const y1 = 50 + 40 * Math.sin(startRad)
                      const x2 = 50 + 40 * Math.cos(endRad)
                      const y2 = 50 + 40 * Math.sin(endRad)
                      
                      const pathD = `M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArc} 1 ${x2} ${y2} Z`
                      
                      const colors = {
                        '纯电动': '#10b981',
                        '插电混动': '#3b82f6',
                        '增程式': '#8b5cf6'
                      }
                      
                      currentAngle = endAngle
                      
                      return (
                        <path
                          key={type}
                          d={pathD}
                          fill={colors[type] || '#6b7280'}
                          className="hover:opacity-80 transition-opacity cursor-pointer"
                        />
                      )
                    })
                  })()}
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-700">{chartData.totalCars}</div>
                    <div className="text-xs text-gray-400">款车型</div>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                {Object.entries(chartData.energyStats).map(([type, count]) => (
                  <div key={type} className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${energyColors[type] || 'bg-gray-400'}`} />
                    <span className="text-sm text-gray-600">{type}</span>
                    <span className="text-xs text-gray-400">({count}款)</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'seats' && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-4">座位数分布</h3>
            <div className="flex items-end justify-center gap-4 h-40">
              {Object.entries(chartData.seatStats)
                .sort(([a], [b]) => Number(a) - Number(b))
                .map(([seats, count]) => {
                  const barHeight = (count / maxSeatCount * 100)
                  const colors = {
                    '4': 'from-blue-400 to-blue-500',
                    '5': 'from-emerald-400 to-emerald-500',
                    '6': 'from-purple-400 to-purple-500',
                    '7': 'from-orange-400 to-orange-500'
                  }
                  
                  return (
                    <div key={seats} className="flex flex-col items-center group">
                      <span className="text-xs text-gray-500 mb-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        {count}款
                      </span>
                      <div
                        className={`w-12 bg-gradient-to-t ${colors[seats] || 'from-gray-400 to-gray-500'} rounded-t-lg transition-all duration-300 group-hover:opacity-80`}
                        style={{ height: `${barHeight}%`, minHeight: '20px' }}
                      />
                      <span className="mt-2 text-sm font-medium text-gray-600">{seats}座</span>
                    </div>
                  )
                })}
            </div>
          </div>
        )}

        {activeTab === 'summary' && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-4">数据摘要</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-emerald-600">{chartData.totalCars}</div>
                <div className="text-xs text-emerald-600 mt-1">可用车型</div>
              </div>
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">{chartData.brands.length}</div>
                <div className="text-xs text-blue-600 mt-1">品牌数量</div>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">{Object.keys(chartData.energyStats).length}</div>
                <div className="text-xs text-purple-600 mt-1">能源类型</div>
              </div>
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {chartData.brands[0] || '-'}
                </div>
                <div className="text-xs text-orange-600 mt-1">最多车型品牌</div>
              </div>
            </div>
            
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <div className="text-xs text-gray-500 mb-2">热门车型</div>
              <div className="flex flex-wrap gap-2">
                {results
                  .filter(r => r.available !== false)
                  .slice(0, 6)
                  .map((car, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-white rounded text-xs text-gray-600 border border-gray-200"
                    >
                      <span className={`w-2 h-2 rounded-full ${
                        car.energy_type === '纯电动' ? 'bg-green-400' :
                        car.energy_type === '插电混动' ? 'bg-blue-400' : 'bg-purple-400'
                      }`} />
                      {car.model_name}
                    </span>
                  ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PriceVisualization
