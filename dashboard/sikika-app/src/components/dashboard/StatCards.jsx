import { useLanguage } from '../../i18n/LanguageContext.jsx'

export default function StatCards() {
  const { t } = useLanguage()

  return (
    <div className="grid sm:grid-cols-3 gap-4">
      <div className="bg-white border border-navy-100 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="w-8 h-8 rounded-lg bg-brand-50 text-brand flex items-center justify-center">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
            </svg>
          </span>
          <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">+12%</span>
        </div>
        <p className="text-[11px] font-semibold text-navy-400 tracking-wide uppercase mb-1">{t('statSmsTotal')}</p>
        <p className="text-2xl font-extrabold text-navy-700">2,845</p>
      </div>

      <div className="bg-white border border-navy-100 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="w-8 h-8 rounded-lg bg-brand-50 text-brand flex items-center justify-center">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 17l6-6 4 4 8-8" />
              <path d="M21 7v6h-6" />
            </svg>
          </span>
          <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">+8%</span>
        </div>
        <p className="text-[11px] font-semibold text-navy-400 tracking-wide uppercase mb-1">{t('statParticipation')}</p>
        <p className="text-2xl font-extrabold text-navy-700">64.2%</p>
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
        <p className="text-[11px] font-semibold text-navy-400 tracking-wide uppercase mb-1">{t('statBillsTracked')}</p>
        <p className="text-2xl font-extrabold text-navy-700">14</p>
      </div>
    </div>
  )
}
