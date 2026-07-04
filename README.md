# Sikika

> Built during the **Democracy & AI Hackathon** — July 4th, 2026
> Hosted by **Mozilla Foundation** & **KamiLimu**

---

## Team

| Name | Role | GitHub |
|------|------|--------|
| [Esther Oyoo] | [Role, Lead Developer] | [@aah3sta] |
| [Maxwell Gitahi] | [Role, Lead Developer] | [@Maxmuthee] |

**Team Name:** [Sikika]
**University:** [Kenyatta University, USIU - Africa]

---

## Problem & User

### Problem Statement

<!-- Describe the core problem in 2-3 sentences. Keep it sharp. -->

> Over 510,000 rural residents aged 35+ in Nakuru County are systematically cut off from county government accountability and public participation processes, as proven by the county's low score of 25 out of 100 on the 2024 County Budget Transparency Survey. This exclusion happens because official accountability documents are published as complex English PDFs online, while over half of rural Kenyans lack the smartphones, internet, or English literacy required to access them. Existing tools like the Jihusishe app fail this demographic by ignoring the deep urban-rural digital divide, leaving a critical need for an offline, local-language channel built for basic feature phones.

### Target User

<!-- Who specifically are you building for? Be as concrete as possible. -->

| Dimension | Detail |
|-----------|--------|
| **Primary user** | A 45-year-old smallholder farmer in rural Nakuru who relies entirely on a basic feature phone. |
| **Tech comfort** | Comfortable with USSD menus and basic SMS; completely offline with no smartphone, web browser, or email access. |
| **Language** | Swahili, Kikuyu - No English literacy |
| **Current workflow** | Hears about local county development plans late via word-of-mouth or local radio, travels miles to centralized barazas to air their views. |

### The Specific Gap

<!-- What exists today? What's the precise gap your solution fills? -->

1. **What's already there:** TISA's Jihusishe digital platform for tracking county data and reporting governance issues.
2. **Why it falls short:** Runs only in English on smartphone apps and web browsers, requiring active internet bundles and text-heavy interactions.
3. **The gap we fill:** Offline, micro-localized Swahili and Kikuyu bill summaries delivered via USSD menus and SMS — no smartphones, internet, or English literacy required.

### Why It Matters

<!-- Connect this to democratic participation. -->

> When rural citizens are locked out of public participation, county governments pass budgets and bills without real community oversight, rendering local voices invisible. Closing this accessibility gap restores a fundamental democratic mechanism: older, rural right-holders can securely review localized county decisions from their homes, log informed feedback and legally hold local duty-bearers accountable.

---

## Run Instructions

### Prerequisites

- Python 3.10+
- [Add any other dependencies: Node.js, Docker, API keys, etc.]

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/[org]/[repo].git
cd [repo]

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Run the project
python src/main.py
```

---

## 📁 Project Structure

```
.
├── README.md                   ← You are here
├── docs/
│   └── problem-statement.md    ← Detailed problem breakdown
├── src/
│   └── main.py                 ← Entry point
├── notebooks/
│   └── exploration.ipynb       ← Experiments & prototyping
├── data/
│   └── .gitkeep                ← Sample / reference data
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## Approach & Architecture

<!--
Briefly describe your approach. What technologies are you using?
Include a simple diagram (ASCII or link) if helpful.

Examples:
- "We use Retrieval-Augmented Generation (RAG) to query county budget PDFs…"
- "We cross-validate enrolment data against capitation flows using…"
-->

```
[User] → [WhatsApp / Web App] → [Backend / API] → [LLM / RAG Pipeline] → [Response]
```

---

## License

MIT © Sikika, 2026

---
