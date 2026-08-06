import DashboardHero from './DashboardHero.jsx'
import BillCard from './BillCard.jsx'
import StatCards from './StatCards.jsx'
import EngagementChart from './EngagementChart.jsx'
import BillStatusTimeline from './BillStatusTimeline.jsx'
import LiveFeed from './LiveFeed.jsx'
import SubmitCTA from './SubmitCTA.jsx'

export default function Dashboard() {
  return (
    <section>
      <DashboardHero />

      <div className="max-w-7xl mx-auto px-5 sm:px-8 mt-4 sm:-mt-8 pb-20">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left / center column */}
          <div className="lg:col-span-2 space-y-6">
            <BillCard />
            <StatCards />
            <EngagementChart />
          </div>

          {/* Right sidebar */}
          <div className="space-y-6">
            <BillStatusTimeline />
            <LiveFeed />
            <SubmitCTA />
          </div>
        </div>
      </div>
    </section>
  )
}
