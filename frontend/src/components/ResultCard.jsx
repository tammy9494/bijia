import { useState } from 'react'
import PriceComparison from './PriceComparison'
import PriceChart from './PriceChart'

function ResultCard({ data, onAddToWatch }) {
  const [isWatched, setIsWatched] = useState(false)
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const energyColors = {
    '纯电动': 'bg-green-100 text-green-700',
    '插电混动': 'bg-blue-100 text-blue-700',
    '增程式': 'bg-purple-100 text-purple-700',
  }

  const isAvailable = data.available !== false

  const openAllPlatforms = () => {
    const allUrls = [data.merchant_url]
    if (data.other_platforms && data.other_platforms.length > 0) {
      data.other_platforms.forEach(platform => {
        allUrls.push(platform.url)
      })
    }
    
    const opened = []
    allUrls.forEach((url) => {
      const win = window.open(url, '_blank')
      if (win) {
        opened.push(url)
      }
    })
    
    if (opened.length < allUrls.length) {
      alert('浏览器阻止了部分弹出窗口，请允许弹出窗口后重试，或手动点击各平台链接')
    }
  }

  const handleAddToWatch = () => {
    if (onAddToWatch && !isWatched) {
      const added = onAddToWatch(data)
      if (added) {
        setIsWatched(true)
      } else {
        alert('该车型已在关注列表中')
      }
    }
  }

  return (
    <div className={`rounded-xl shadow-sm border p-5 transition-shadow ${
      isAvailable
        ? 'bg-white border-gray-100 hover:shadow-md'
        : 'bg-gray-50 border-gray-200 opacity-70'
    }`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-gray-500">{data.brand}</span>
            <span className="text-gray-300">·</span>
            <span className="text-sm text-gray-500">{data.series}</span>
          </div>
          <h3 className={`text-lg font-semibold truncate ${isAvailable ? 'text-gray-800' : 'text-gray-500'}`} title={data.model_name}>
            {data.model_name}
          </h3>
          <div className="flex flex-wrap items-center gap-2 mt-2">
            <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${energyColors[data.energy_type] || 'bg-gray-100 text-gray-600'}`}>
              {data.energy_type}
            </span>
            {data.range_km && (
              <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                续航 {data.range_km}km
              </span>
            )}
            <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
              {data.seats}座
            </span>
          </div>
        </div>

        <div className="text-right flex-shrink-0">
          {isAvailable ? (
            <div>
              <span className="inline-block px-3 py-1 rounded-md text-sm font-medium bg-emerald-100 text-emerald-700">
                有车
              </span>
              <button
                onClick={handleAddToWatch}
                disabled={isWatched}
                className={`mt-2 w-full px-3 py-1.5 text-xs rounded-lg transition-all ${
                  isWatched 
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                    : 'bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200'
                }`}
              >
                {isWatched ? '✓ 已关注' : '+ 关注价格'}
              </button>
            </div>
          ) : (
            <span className="inline-block px-3 py-1 rounded-md text-sm font-medium bg-gray-200 text-gray-500">
              该平台暂无此车
            </span>
          )}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-gray-100">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm text-gray-500">比价平台：</span>
          
          <button
            onClick={openAllPlatforms}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-orange-600 bg-orange-50 rounded-lg hover:bg-orange-100 transition-all border border-orange-200"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            一键比价
          </button>
          
          <a
            href={data.merchant_url}
            target="_blank"
            rel="noopener noreferrer"
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg transition-all ${
              isAvailable 
                ? 'text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200' 
                : 'text-gray-500 bg-gray-100 hover:bg-gray-200 border border-gray-200'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${isAvailable ? 'bg-emerald-500 animate-pulse' : 'bg-gray-400'}`} />
            一嗨租车
            <span className={`text-xs px-1.5 py-0.5 rounded ${isAvailable ? 'bg-emerald-200 text-emerald-800' : 'bg-gray-200 text-gray-500'}`}>
              {isAvailable ? '有车' : '无车'}
            </span>
          </a>
          
          {data.other_platforms && data.other_platforms.map((platform, index) => (
            <a
              key={index}
              href={platform.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-all border border-blue-200"
            >
              <span className="w-2 h-2 rounded-full bg-blue-400" />
              {platform.name}
              <span className="text-xs px-1.5 py-0.5 rounded bg-blue-200 text-blue-700">
                去比价
              </span>
            </a>
          ))}
        </div>
        
        {/* 使用提示 */}
        <div className="mt-2 text-xs text-gray-400 flex items-center gap-1">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          点击平台链接可跳转到对应平台查看实时价格
        </div>
        
        <div className="flex items-center gap-4 text-sm text-gray-500 mt-2">
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {data.city}
          </span>
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {formatDate(data.pickup_time)} - {formatDate(data.return_time)}
          </span>
        </div>
        
        {/* 价格对比工具 */}
        {data.other_platforms && data.other_platforms.length > 0 && (
          <div className="mt-3 flex flex-col gap-3">
            <PriceComparison car={data} platforms={[{ name: '一嗨租车' }, ...data.other_platforms]} />
            <PriceChart carName={data.model_name} platforms={[{ name: '一嗨租车' }, ...data.other_platforms]} />
          </div>
        )}
      </div>
    </div>
  )
}

export default ResultCard
