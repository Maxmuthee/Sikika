import { useState, useEffect } from 'react'
import { useLanguage } from '../../i18n/LanguageContext.jsx'

export default function BillCard() {
  const { t } = useLanguage()
  const [bill, setBill] = useState(undefined) // undefined = loading, null = none

  useEffect(() => {
    fetch('/api/dashboard-stats')
      .then((r) => r.json())
      .then((d) => setBill(d.featured || null))
      .catch(() => setBill(null))
  }, [])

  return (
    <div className="bg-white rounded-2xl shadow-md border border-slate-200 overflow-hidden">
      <div className="flex flex-col md:flex-row items-stretch md:min-h-[320px]">
        <div className="md:w-1/2 bg-amber-50 h-48 md:h-auto md:min-h-[220px] relative">
          <img
            src="/images/bill-produce.jpg"
            alt="Agricultural produce crate"
            className="w-full h-full object-cover absolute inset-0"
          />
        </div>

        <div className="md:w-1/2 p-5 flex flex-col justify-between">
          {bill === undefined && (
            <p className="text-sm text-slate-400 py-10 text-center">Loading…</p>
          )}
          {bill === null && (
            <p className="text-sm text-slate-400 py-10 text-center">{t('noBillYet')}</p>
          )}
          {bill && (
            <>
              <div>
                <span className="inline-block text-[10px] font-bold text-[#EA580C] tracking-wide uppercase mb-2">
                  {t('activeLegislation')} · {bill.ward}
                </span>

                <div className="flex items-start justify-between gap-2 mb-3">
                  <h3 className="font-bold text-[#0F172A] text-lg leading-snug">{bill.title}</h3>
                </div>

                <div className="space-y-2 mb-4">
                  <div>
                    <div className="flex justify-between text-xs font-medium text-slate-500 mb-1">
                      <span>{t('publicSupport')}</span>
                      <span className="text-[#0F172A] font-bold">{bill.support_pct}%</span>
                    </div>
                    <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-[#EA580C] rounded-full" style={{ width: `${bill.support_pct}%` }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs font-medium text-slate-500 mb-1">
                      <span>{t('opposition')}</span>
                      <span className="text-[#0F172A] font-bold">{bill.oppose_pct}%</span>
                    </div>
                    <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-slate-400 rounded-full" style={{ width: `${bill.oppose_pct}%` }} />
                    </div>
                  </div>
                </div>

                {bill.ai_insight && (
                  <div className="bg-slate-50 rounded-xl p-3.5 mb-4 border border-slate-100">
                    <span className="inline-block text-[10px] font-bold text-[#EA580C] mb-1">{t('aiInsightTag')}</span>
                    <p className="text-xs text-slate-600 leading-relaxed">{bill.ai_insight}</p>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between pt-2">
                <span className="flex items-center gap-1.5 text-xs font-medium text-slate-500">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
                  </svg>
                  {bill.participants} {t('citizensEngaged')}
                </span>
                <button className="flex items-center gap-1.5 bg-[#EA580C] hover:bg-orange-700 text-white text-xs font-semibold px-3.5 py-2 rounded-lg transition">
                  {t('readFullText')}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
