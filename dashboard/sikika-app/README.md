# SIKIKA — Civic Transparency Platform

A React + Tailwind CSS rebuild of the SIKIKA landing page and Civic
Transparency Dashboard, matching the uploaded Visily mockups.

## Getting started

```bash
npm install
npm run dev       # local dev server
npm run build     # production build -> dist/
```

## Project structure

```
sikika-app/
├─ index.html                     # Vite entry HTML
├─ tailwind.config.js             # navy / brand (orange) color palette
├─ postcss.config.js
├─ vite.config.js
├─ public/
│  └─ images/                     
└─ src/
   ├─ main.jsx                    # React root, wraps App in LanguageProvider
   ├─ App.jsx                     # Assembles all page sections
   ├─ index.css                   # Tailwind directives + custom animations
   ├─ i18n/
   │  ├─ translations.js          # All EN/SW copy in one place
   │  └─ LanguageContext.jsx      # useLanguage() hook + toggle logic
   └─ components/
      ├─ Header.jsx
      ├─ LanguageToggle.jsx       # the Swahili | English pill
      ├─ Hero.jsx
      ├─ Mission.jsx
      ├─ CoreFunctions.jsx
      ├─ CTABanner.jsx
      ├─ ValuesStrip.jsx
      ├─ Footer.jsx
      └─ dashboard/
         ├─ Dashboard.jsx         # wraps the whole dashboard section
         ├─ DashboardHero.jsx     # teal gradient header + filters
         ├─ BillCard.jsx
         ├─ StatCards.jsx
         ├─ EngagementChart.jsx   # plain CSS/JS bar chart, no chart library
         ├─ BillStatusTimeline.jsx
         ├─ LiveFeed.jsx          # includes working search-filter state
         └─ SubmitCTA.jsx
```

## Language toggle

Click **Swahili | English** next to the top badge on the hero. It flips a
`lang` state in `LanguageContext.jsx`, and every component reads its copy
through `t('key')`. All strings live in `src/i18n/translations.js` — edit
them there, no need to touch component files.

## Adding your images

See `public/images/README.md` for the exact filenames each component
expects (`hero-village.jpg`, `mission-illustration.jpg`,
`bill-produce.jpg`). Drop files with those names into `public/images/` and
they'll render immediately — no code changes needed.

## Color palette

Defined in `tailwind.config.js`:
- `navy` (`#0B2545`) — primary text / dark sections
- `brand` (`#EA580C`) — orange accent, buttons, highlights
- White — base background throughout

## Notes

- Pure Tailwind utility classes, no external UI kit.
- The weekly engagement chart is hand-rolled (divs + CSS `scaleY` animation) — swap in Recharts/Chart.js later if you want tooltips or live data binding.
- The Live SMS Feed search box is already wired to functional React state (`LiveFeed.jsx`) and filters citizen messages as you type.
