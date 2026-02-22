function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 animate-pulse">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <div className="h-4 w-12 bg-gray-200 rounded"></div>
            <div className="h-4 w-16 bg-gray-200 rounded"></div>
          </div>
          <div className="h-6 w-48 bg-gray-300 rounded mb-3"></div>
          <div className="flex gap-2">
            <div className="h-5 w-14 bg-gray-200 rounded"></div>
            <div className="h-5 w-20 bg-gray-200 rounded"></div>
            <div className="h-5 w-10 bg-gray-200 rounded"></div>
          </div>
        </div>
        <div className="text-right">
          <div className="h-3 w-10 bg-gray-200 rounded mb-1"></div>
          <div className="h-8 w-16 bg-gray-300 rounded mb-2"></div>
          <div className="h-4 w-14 bg-gray-200 rounded"></div>
        </div>
      </div>
      <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between">
        <div className="flex gap-4">
          <div className="h-4 w-16 bg-gray-200 rounded"></div>
          <div className="h-4 w-10 bg-gray-200 rounded"></div>
          <div className="h-4 w-32 bg-gray-200 rounded"></div>
        </div>
        <div className="h-8 w-20 bg-gray-200 rounded-lg"></div>
      </div>
    </div>
  )
}

export default SkeletonCard
