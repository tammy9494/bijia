import { useState, useCallback, useRef } from 'react'
import SearchForm from './components/SearchForm'
import ResultList from './components/ResultList'
import PriceVisualization from './components/PriceVisualization'
import WatchList from './components/WatchList'
import usePriceMonitor from './hooks/usePriceMonitor'
import { searchRentalPrices } from './services/api'

function App() {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searchMeta, setSearchMeta] = useState(null)
  const [watchList, setWatchList] = useState([])
  const watchListRef = useRef(null)

  const handlePriceChange = useCallback((changeInfo) => {
    if (watchListRef.current) {
      watchListRef.current.addNotification({
        type: 'price_change',
        message: changeInfo.message,
        modelName: changeInfo.modelName,
        oldPrice: changeInfo.oldPrice,
        newPrice: changeInfo.newPrice,
        change: changeInfo.change
      })
      
      if (changeInfo.watchId) {
        watchListRef.current.updateWatchItemPrice(changeInfo.watchId, changeInfo.newPrice)
      }
    }
  }, [])

  const { isMonitoring, lastCheckTime, monitorStats, startMonitoring, stopMonitoring, manualCheck } = 
    usePriceMonitor(watchList, handlePriceChange)

  const handleSearch = async (searchParams) => {
    setLoading(true)
    setError(null)
    setResults([])
    setSearchMeta(null)

    try {
      const data = await searchRentalPrices(searchParams)
      if (data.success) {
        setResults(data.data)
        setSearchMeta({
          searchType: data.search_type,
          message: data.message,
        })
      } else {
        setError(data.message || '查询失败')
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || '网络错误，请稍后重试'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleWatchChange = useCallback((list) => {
    setWatchList(list)
  }, [])

  const handleAddToWatch = useCallback((car) => {
    if (watchListRef.current) {
      return watchListRef.current.addToWatch(car)
    }
    return false
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-emerald-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <div className="flex items-center justify-center gap-4 mb-2">
            <h1 className="text-4xl font-bold text-gray-800">
              新能源汽车租赁比价
            </h1>
          </div>
          <p className="text-gray-500">
            一键对比多个平台的新能源车租赁价格 · AI Agent智能监控
          </p>
        </header>

        <div className="max-w-5xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <SearchForm onSearch={handleSearch} disabled={loading} />
            <WatchList ref={watchListRef} onWatchChange={handleWatchChange} />
          </div>

          {isMonitoring && (
            <div className="mb-4 p-3 bg-gradient-to-r from-emerald-50 to-blue-50 rounded-lg border border-emerald-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
                    <div className="absolute inset-0 w-3 h-3 bg-emerald-500 rounded-full animate-ping"></div>
                  </div>
                  <span className="text-sm font-medium text-emerald-700">AI Agent监控中</span>
                  <span className="text-xs text-gray-500">
                    已检查 {monitorStats.totalChecks} 次 · 发现 {monitorStats.priceChanges} 次价格变动
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={manualCheck}
                    className="px-3 py-1 text-xs bg-white text-emerald-600 rounded border border-emerald-200 hover:bg-emerald-50"
                  >
                    立即检查
                  </button>
                  <button
                    onClick={stopMonitoring}
                    className="px-3 py-1 text-xs bg-white text-red-500 rounded border border-red-200 hover:bg-red-50"
                  >
                    停止监控
                  </button>
                </div>
              </div>
              {lastCheckTime && (
                <div className="text-xs text-gray-400 mt-1">
                  上次检查: {lastCheckTime}
                </div>
              )}
            </div>
          )}

          {!isMonitoring && watchList && watchList.length > 0 && (
            <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm text-gray-600">
                    已关注 {watchList.length} 个车型，点击开始AI监控
                  </span>
                </div>
                <button
                  onClick={startMonitoring}
                  className="px-4 py-1.5 text-sm bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
                >
                  启动AI监控
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600">{error}</p>
            </div>
          )}

          {searchMeta && (
            <div className="mt-6 flex items-center gap-2 text-sm text-gray-500">
              <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                searchMeta.searchType === 'exact'
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-amber-100 text-amber-700'
              }`}>
                {searchMeta.searchType === 'exact' ? '精确匹配' : '模糊搜索'}
              </span>
              <span>{searchMeta.message}</span>
            </div>
          )}

          {results.length > 0 && (
            <PriceVisualization results={results} />
          )}

          <ResultList results={results} loading={loading} onAddToWatch={handleAddToWatch} />

          {results.length > 0 && (
            <p className="mt-4 text-xs text-gray-400 text-center">
              * 车型数据来自一嗨租车，实际价格因取还车地点和时间不同会有差异，请点击「查看价格并预订」前往平台确认。
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
