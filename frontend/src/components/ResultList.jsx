import ResultCard from './ResultCard'
import SkeletonCard from './SkeletonCard'

function ResultList({ results, loading, onAddToWatch }) {
  if (loading) {
    return (
      <div className="mt-6 space-y-4">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    )
  }

  if (results.length === 0) {
    return null
  }

  const grouped = {}
  results.forEach((item) => {
    const key = item.model_name
    if (!grouped[key]) {
      grouped[key] = []
    }
    grouped[key].push(item)
  })

  Object.values(grouped).forEach((group) => {
    group.sort((a, b) => {
      const aAvail = a.available !== false ? 0 : 1
      const bAvail = b.available !== false ? 0 : 1
      return aAvail - bAvail
    })
  })

  const sortedEntries = Object.entries(grouped).sort(([, a], [, b]) => {
    const aHasReal = a.some(i => i.available !== false) ? 0 : 1
    const bHasReal = b.some(i => i.available !== false) ? 0 : 1
    return aHasReal - bHasReal
  })

  return (
    <div className="mt-6 space-y-6">
      {sortedEntries.map(([modelName, items]) => (
        <div key={modelName}>
          {Object.keys(grouped).length > 1 && (
            <h3 className="text-base font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span className="w-1 h-4 bg-emerald-500 rounded-full inline-block"></span>
              {modelName}
              <span className="text-sm font-normal text-gray-400">({items.length} 条报价)</span>
            </h3>
          )}
          <div className="space-y-3">
            {items.map((item, index) => (
              <ResultCard key={`${item.merchant}-${index}`} data={item} onAddToWatch={onAddToWatch} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export default ResultList
