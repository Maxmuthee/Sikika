import { useState, useEffect } from 'react'
import DashboardHero from './DashboardHero.jsx'
import BillCard from './BillCard.jsx'
import StatCards from './StatCards.jsx'
import EngagementChart from './EngagementChart.jsx'
import BillStatusTimeline from './BillStatusTimeline.jsx'
import LiveFeed from './LiveFeed.jsx'
import BillsList from './BillsList.jsx'
import SubmitCTA from './SubmitCTA.jsx'

export default function Dashboard() {
  // null = All Sub-Counties. When set, every widget below is scoped to that area.
  const [selected, setSelected] = useState(null)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    const qs = selected ? `?ward=${encodeURIComponent(selected)}` : ''
    fetch(`/api/dashboard-stats${qs}`)
      .then((r) => r.json())
      .then(setStats)
      .catch(() => setStats(null))
  }, [selected])

  return (
    <section>
      <DashboardHero selected={selected} onSelect={setSelected} />

      <div className="max-w-7xl mx-auto px-5 sm:px-8 mt-8 sm:mt-10 pb-20">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left / center column */}
          <div className="lg:col-span-2 space-y-6">
            <BillCard bill={stats?.featured} />
            <StatCards stats={stats} />
            <EngagementChart engagement={stats?.engagement} />
            <BillsList bills={stats?.bills} />
          </div>

          {/* Right sidebar */}
          <div className="space-y-6">
            <BillStatusTimeline bill={stats?.featured} />
            <LiveFeed feedback={stats?.feedback} />
            <SubmitCTA />
          </div>
        </div>
      </div>
    </section>
  )
}
