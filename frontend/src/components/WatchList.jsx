import { useState, useEffect, forwardRef, useImperativeHandle } from 'react'

const WatchList = forwardRef(function WatchList({ onWatchChange }, ref) {
  const [watchList, setWatchList] = useState(() => {
    const saved = localStorage.getItem('watch_list')
    return saved ? JSON.parse(saved) : []
  })
  const [showPanel, setShowPanel] = useState(false)
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    localStorage.setItem('watch_list', JSON.stringify(watchList))
    if (onWatchChange) {
      onWatchChange(watchList)
    }
  }, [watchList, onWatchChange])

  useEffect(() => {
    const saved = localStorage.getItem('price_notifications')
    if (saved) {
      setNotifications(JSON.parse(saved))
    }
  }, [])

  const addToWatch = (car) => {
    const exists = watchList.find(item => 
      item.model_name === car.model_name && item.city === car.city
    )
    if (!exists) {
      const watchItem = {
        id: Date.now().toString(),
        model_name: car.model_name,
        brand: car.brand,
        city: car.city,
        pickup_time: car.pickup_time,
        return_time: car.return_time,
        added_at: new Date().toLocaleString('zh-CN'),
        last_price: null,
        price_history: []
      }
      setWatchList(prev => [...prev, watchItem])
      return true
    }
    return false
  }

  const removeFromWatch = (id) => {
    setWatchList(prev => prev.filter(item => item.id !== id))
  }

  const clearNotifications = () => {
    setNotifications([])
    localStorage.removeItem('price_notifications')
  }

  const addNotification = (notification) => {
    const newNotification = {
      id: Date.now().toString(),
      ...notification,
      created_at: new Date().toLocaleString('zh-CN')
    }
    setNotifications(prev => {
      const updated = [newNotification, ...prev].slice(0, 20)
      localStorage.setItem('price_notifications', JSON.stringify(updated))
      return updated
    })
    
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('价格变动提醒', {
        body: notification.message,
        icon: '/favicon.ico'
      })
    }
  }

  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      if (permission === 'granted') {
        alert('已开启浏览器通知，价格变动时会推送提醒')
      }
    }
  }

  const updateWatchItemPrice = (id, price) => {
    setWatchList(prev => prev.map(item => {
      if (item.id === id) {
        const newHistory = [...(item.price_history || []), {
          price,
          date: new Date().toLocaleDateString('zh-CN'),
          time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
        }].slice(-10)
        
        return {
          ...item,
          last_price: price,
          price_history: newHistory,
          last_check: new Date().toLocaleString('zh-CN')
        }
      }
      return item
    }))
  }

  useImperativeHandle(ref, () => ({
    addToWatch,
    removeFromWatch,
    addNotification,
    clearNotifications,
    updateWatchItemPrice,
    getWatchList: () => watchList
  }))

  return (
    <div className="relative">
      <button
        onClick={() => setShowPanel(!showPanel)}
        className="relative inline-flex items-center gap-2 px-4 py-2 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-all"
      >
        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <span className="text-sm font-medium text-gray-700">价格监控</span>
        {notifications.length > 0 ? (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-orange-500 text-white text-xs rounded-full flex items-center justify-center animate-pulse">
            {notifications.length}
          </span>
        ) : watchList.length > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-emerald-500 text-white text-xs rounded-full flex items-center justify-center">
            {watchList.length}
          </span>
        )}
      </button>

      {showPanel && (
        <div className="absolute right-0 top-12 w-96 bg-white rounded-xl shadow-xl border border-gray-200 z-50 overflow-hidden">
          <div className="p-4 bg-gradient-to-r from-emerald-50 to-blue-50 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-800">价格监控列表</h3>
              <div className="flex items-center gap-2">
                <button
                  onClick={requestNotificationPermission}
                  className="text-xs text-blue-500 hover:text-blue-600"
                  title="开启浏览器通知"
                >
                  开启通知
                </button>
                <button
                  onClick={() => setShowPanel(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-1">添加关注后，系统会自动监控价格变化</p>
          </div>

          {notifications.length > 0 && (
            <div className="p-3 bg-orange-50 border-b border-orange-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-orange-700">价格变动通知</span>
                <button
                  onClick={clearNotifications}
                  className="text-xs text-orange-500 hover:text-orange-600"
                >
                  清空
                </button>
              </div>
              <div className="max-h-24 overflow-y-auto space-y-1">
                {notifications.slice(0, 5).map(n => (
                  <div key={n.id} className="text-xs text-orange-600 bg-white p-2 rounded">
                    {n.message}
                    <span className="text-orange-400 ml-2">{n.created_at}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="max-h-80 overflow-y-auto">
            {watchList.length === 0 ? (
              <div className="p-6 text-center text-gray-400">
                <svg className="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p className="text-sm">暂无关注的车型</p>
                <p className="text-xs mt-1">点击车型卡片的"关注"按钮添加</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {watchList.map(item => (
                  <div key={item.id} className="p-3 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm text-gray-800 truncate">{item.model_name}</div>
                        <div className="text-xs text-gray-500 mt-0.5">{item.brand} · {item.city}</div>
                        <div className="text-xs text-gray-400 mt-1">
                          取车: {new Date(item.pickup_time).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}
                        </div>
                        {item.last_price && (
                          <div className="mt-1 inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-50 rounded text-xs text-emerald-600">
                            最新价格: ¥{item.last_price}/天
                          </div>
                        )}
                        {item.last_check && (
                          <div className="text-xs text-gray-400 mt-1">
                            上次检查: {item.last_check}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => removeFromWatch(item.id)}
                        className="text-gray-400 hover:text-red-500 transition-colors"
                        title="取消关注"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {watchList.length > 0 && (
            <div className="p-3 bg-gray-50 border-t border-gray-100">
              <p className="text-xs text-gray-400 text-center">
                系统会自动监控价格变化并推送提醒
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
})

export default WatchList
