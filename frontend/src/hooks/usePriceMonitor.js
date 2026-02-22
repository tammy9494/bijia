import { useState, useEffect, useCallback, useRef } from 'react'

const MONITOR_INTERVAL = 5 * 60 * 1000

function usePriceMonitor(watchList, onPriceChange) {
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [lastCheckTime, setLastCheckTime] = useState(null)
  const [monitorStats, setMonitorStats] = useState({
    totalChecks: 0,
    priceChanges: 0,
    lastChangeTime: null
  })
  const intervalRef = useRef(null)
  const statsRef = useRef(monitorStats)

  const checkPrices = useCallback(async () => {
    if (!watchList || watchList.length === 0) return

    console.log('[PriceMonitor] Starting price check for', watchList.length, 'items')
    
    for (const item of watchList) {
      try {
        const response = await fetch('/api/rental/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: item.model_name,
            city: item.city,
            pickup_time: item.pickup_time,
            return_time: item.return_time
          })
        })
        
        const data = await response.json()
        
        if (data.success && data.data && data.data.length > 0) {
          const carData = data.data.find(c => 
            c.model_name === item.model_name || 
            c.model_name.includes(item.model_name) ||
            item.model_name.includes(c.model_name)
          )
          
          if (carData && carData.daily_price) {
            const newPrice = carData.daily_price
            const oldPrice = item.last_price
            
            if (oldPrice !== null && newPrice !== oldPrice) {
              const change = newPrice - oldPrice
              const changePercent = ((change / oldPrice) * 100).toFixed(1)
              
              statsRef.current = {
                ...statsRef.current,
                priceChanges: statsRef.current.priceChanges + 1,
                lastChangeTime: new Date().toLocaleString('zh-CN')
              }
              setMonitorStats(statsRef.current)
              
              if (onPriceChange) {
                onPriceChange({
                  watchId: item.id,
                  modelName: item.model_name,
                  oldPrice,
                  newPrice,
                  change,
                  changePercent,
                  message: `${item.model_name} 价格${change > 0 ? '上涨' : '下降'} ¥${Math.abs(change)} (${change > 0 ? '+' : ''}${changePercent}%)，现价 ¥${newPrice}/天`,
                  city: item.city
                })
              }
            }
          }
        }
      } catch (error) {
        console.error('[PriceMonitor] Error checking price for', item.model_name, error)
      }
    }
    
    statsRef.current = {
      ...statsRef.current,
      totalChecks: statsRef.current.totalChecks + 1
    }
    setMonitorStats(statsRef.current)
    setLastCheckTime(new Date().toLocaleString('zh-CN'))
    
    localStorage.setItem('monitor_stats', JSON.stringify(statsRef.current))
  }, [watchList, onPriceChange])

  const startMonitoring = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
    
    setIsMonitoring(true)
    console.log('[PriceMonitor] Started monitoring')
    
    checkPrices()
    
    intervalRef.current = setInterval(checkPrices, MONITOR_INTERVAL)
    
    localStorage.setItem('monitor_status', 'running')
  }, [checkPrices])

  const stopMonitoring = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setIsMonitoring(false)
    console.log('[PriceMonitor] Stopped monitoring')
    localStorage.setItem('monitor_status', 'stopped')
  }, [])

  const manualCheck = useCallback(() => {
    console.log('[PriceMonitor] Manual check triggered')
    checkPrices()
  }, [checkPrices])

  useEffect(() => {
    const savedStats = localStorage.getItem('monitor_stats')
    if (savedStats) {
      const parsed = JSON.parse(savedStats)
      statsRef.current = parsed
      setMonitorStats(parsed)
    }
    
    const savedStatus = localStorage.getItem('monitor_status')
    if (savedStatus === 'running' && watchList.length > 0) {
      startMonitoring()
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  useEffect(() => {
    if (isMonitoring && watchList.length === 0) {
      stopMonitoring()
    }
  }, [watchList.length, isMonitoring, stopMonitoring])

  return {
    isMonitoring,
    lastCheckTime,
    monitorStats,
    startMonitoring,
    stopMonitoring,
    manualCheck
  }
}

export default usePriceMonitor
