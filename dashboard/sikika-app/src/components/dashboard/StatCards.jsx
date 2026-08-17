import { useLanguage } from '../../i18n/LanguageContext.jsx'

export default function StatCards({ stats }) {
  const { t } = useLanguage()

  const num = (n) => (n == null ? '—' : Number(n).toLocaleString())

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div className="bg-white border border-navy-100 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="w-8 h-8 rounded-lg bg-brand-50 text-brand flex items-center justify-center">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
            </svg>
          </span>
        </div>
        <p className="text-xs font-semibold text-navy-400 tracking-wide uppercase mb-1">{t('statSmsTotal')}</p>
        <p className="text-2xl font-extrabold text-navy-700">{num(stats?.sms_total)}</p>
      </div>

      <div className="bg-white border border-navy-100 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="w-8 h-8 rounded-lg bg-brand-50 text-brand flex items-center justify-center">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 17l6-6 4 4 8-8" />
              <path d="M21 7v6h-6" />
            </svg>
          </span>
        </div>
        <p className="text-xs font-semibold text-navy-400 tracking-wide uppercase mb-1">{t('statParticipation')}</p>
        <p className="text-2xl font-extrabold text-navy-700">{stats == null ? '—' : `${stats.participation_pct}%`}</p>
      </div>

      <div className="bg-white border border-navy-100 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="w-8 h-8 rounded-lg bg-brand-50 text-brand flex items-center justify-center">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
              <path d="M14 2v6h6" />
            </svg>
          </span>
        </div>
        <p className="text-xs font-semibold text-navy-400 tracking-wide uppercase mb-1">{t('statBillsTracked')}</p>
        <p className="text-2xl font-extrabold text-navy-700">{num(stats?.bills_tracked)}</p>
      </div>
    </div>
  )
}
