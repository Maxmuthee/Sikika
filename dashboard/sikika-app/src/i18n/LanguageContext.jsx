import React, { createContext, useContext, useState, useMemo } from 'react'
import translations from './translations.js'

const LanguageContext = createContext(null)

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState('en')

  const toggleLang = () => setLang((prev) => (prev === 'en' ? 'sw' : 'en'))

  // t() looks up a key in the current language's dictionary
  const value = useMemo(() => {
    const t = (key) => translations[lang][key] ?? translations.en[key] ?? key
    return { lang, setLang, toggleLang, t }
  }, [lang])

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

// Custom hook: const { t, lang, toggleLang } = useLanguage()
export function useLanguage() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLanguage must be used within a LanguageProvider')
  return ctx
}
