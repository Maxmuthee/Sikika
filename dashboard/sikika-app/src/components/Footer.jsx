import { useState } from 'react'
import { useLanguage } from '../i18n/LanguageContext.jsx'

const LEGAL = {
  privacy: {
    title: 'Data Privacy (ODPC)',
    body: `Sikika complies with Kenya's Data Protection Act, 2019 and follows the standards of the Office of the Data Protection Commissioner (ODPC).\n\nWe collect only what is needed to deliver civic alerts: your phone number (to send SMS) and a one-way hashed form of your National ID (to ensure one person, one vote). Your ID is never stored in raw form and is never shown anywhere.\n\nVotes are recorded under a separate anonymous identifier that cannot be linked back to your phone or ID. We never sell or share your data with third parties.`,
  },
  terms: {
    title: 'Terms of Use',
    body: `Sikika is a non-partisan civic-education service. Information is simplified from official county and national documents for accessibility and may be summarised; always confirm details with the official source.\n\nParticipation (votes and feedback) is voluntary and is shared with county officials only in aggregate, anonymous form.`,
  },
  accessibility: {
    title: 'Accessibility',
    body: `Sikika is built for basic feature phones over USSD and SMS. No smartphone, internet or English literacy required. Content is offered in Kiswahili, Gikuyu, and English.\n\nThis web dashboard aims to meet WCAG 2.1 AA. If you encounter a barrier, contact info@sikika.go.ke.`,
  },
}

export default function Footer() {
  const { t } = useLanguage()
  const [modal, setModal] = useState(null)

  return (
    <footer className="border-t border-navy-100 bg-white">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 py-14 grid sm:grid-cols-3 gap-10">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-7 h-7 rounded-md bg-brand flex items-center justify-center text-white">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m3 11 18-5v12L3 13v-2z" />
                <path d="M11.6 16.8a3 3 0 1 1-5.8-1.6" />
                <path d="M22 9a4 4 0 0 1 0 6" />
              </svg>
            </div>
            <span className="font-extrabold text-navy-700">SIKIKA</span>
          </div>
          <p className="text-sm text-navy-400 leading-relaxed max-w-xs">{t('footerBody')}</p>
        </div>

        <div>
          <p className="text-xs font-bold text-navy-700 tracking-wide mb-4">{t('contactUs')}</p>
          <ul className="space-y-3 text-sm text-navy-400">
            <li className="flex items-center gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4h16v16H4z" />
                <path d="M4 4l8 8 8-8" />
              </svg>
              info@sikika.go.ke
            </li>
            <li className="flex items-center gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6A19.8 19.8 0 012.1 4.2 2 2 0 014.1 2h3a2 2 0 012 1.7c.1.9.3 1.8.6 2.7a2 2 0 01-.4 2.1L8 9.9a16 16 0 006 6l1.5-1.3a2 2 0 012.1-.4c.9.3 1.8.5 2.7.6a2 2 0 011.7 2.1z" />
              </svg>
              +254 20 123 4567
            </li>
            <li className="flex items-center gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 0118 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              Nakuru City, Kenya
            </li>
          </ul>
        </div>

        <div>
          <p className="text-xs font-bold text-navy-700 tracking-wide mb-4">{t('legal')}</p>
          <ul className="space-y-3 text-sm text-navy-400">
            <li>
              <button onClick={() => setModal('privacy')} className="hover:text-brand text-left">
                {t('privacy')}
              </button>
            </li>
            <li>
              <button onClick={() => setModal('terms')} className="hover:text-brand text-left">
                {t('terms')}
              </button>
            </li>
            <li>
              <button onClick={() => setModal('accessibility')} className="hover:text-brand text-left">
                {t('accessibility')}
              </button>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-navy-100 py-5">
        <p className="text-center text-xs text-navy-300">{t('copyright')}</p>
      </div>

      {modal && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50"
          onClick={() => setModal(null)}
        >
          <div
            className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-extrabold text-navy-700 text-lg">{LEGAL[modal].title}</h3>
              <button
                onClick={() => setModal(null)}
                aria-label="Close"
                className="text-navy-400 hover:text-navy-700 text-2xl leading-none"
              >
                ×
              </button>
            </div>
            <p className="text-sm text-navy-500 leading-relaxed whitespace-pre-line">{LEGAL[modal].body}</p>
            <button
              onClick={() => setModal(null)}
              className="mt-5 w-full bg-brand text-white text-sm font-semibold py-2.5 rounded-lg hover:bg-orange-700 transition"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </footer>
  )
}
