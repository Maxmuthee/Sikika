# Sikika

> Built during the **Democracy & AI Hackathon** — July 4th, 2026
> Hosted by **Mozilla Foundation** & **KamiLimu**

---

## Team

| Name | Role | GitHub |
|------|------|--------|
| [Esther Oyoo] | [Role, Lead Developer] | [@aah3sta] |
| [Maxwell Gitahi] | [Role, Developer] | [@Maxmuthee] |

**Team Name:** [Sikika]
**University:** [Kenyatta University, USIU - Africa]

---

## Problem & User

### Problem Statement

<!-- Describe the core problem in 2-3 sentences. Keep it sharp. -->

> [Rural residents aged 35 and above in Nakuru County face systematic exclusion from county government accountability and public participation. With over 510,000 individuals in this demographic (KNBS, 2019) largely underserved by existing civic technology, they are unable to track or influence how public funds affecting their livelihoods are allocated. Nakuru County scored only 25 out of 100 points on public participation feedback in the 2024 County Budget Transparency Survey, confirming that community input is collected but rarely translated into visible action. This problem is primarily caused by the absence of a lightweight, offline, local-language platform capable of translating complex county budget documents and broadcasting participation notices via SMS or USSD on basic feature phones. Supported by Communications Authority of Kenya data, the urban-rural digital divide locks out low-literacy, Kikuyu and Swahili-speaking adults from such processes. Despite Jihusishe's ambition to connect citizens with government accountability data, it requires smartphones, stable internet and English literacy; channels this population cannot access. An AI-powered SMS and USSD platform delivering simplified, mother-tongue accountability information to feature phones could meaningfully expand civic participation in Nakuru County, while ensuring all verification data is hashed, anonymised and never shared with third parties.]

### Target User

<!-- Who specifically are you building for? Be as concrete as possible. -->

| Dimension | Detail |
|-----------|--------|
| **Primary user** | [e.g. A smallholder farmer in Migori County who uses WhatsApp daily] |
| **Tech comfort** | [e.g. Comfortable with WhatsApp voice notes and text; no email] |
| **Language** | [e.g. Swahili, Sheng, Dholuo — not English] |
| **Current workflow** | [e.g. Hears about projects from local radio or baraza, has no way to verify] |

### The Specific Gap

<!-- What exists today? What's the precise gap your solution fills? -->

1. **What's already there:** [e.g. International Budget Partnership Kenya's County Budget Transparency Survey; Auditor-General audit reports]
2. **Why it falls short:** [e.g. Published as 200+ page English PDFs; require desktop browser, stable internet, and advanced literacy]
3. **The gap we fill:** [e.g. Real-time, simplified Swahili/Sheng summaries delivered on WhatsApp — no PDFs, no English, no desktop required]

### Why It Matters

<!-- Connect this to democratic participation. -->

> [e.g. When rural citizens can't track county spending, projects stall, funds divert, and the accountability loop between citizen and government breaks. Closing this information gap restores a basic democratic feedback mechanism: informed citizens can ask better questions, demand answers, and vote accordingly.]

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

MIT © [Sikika], 2026

---
