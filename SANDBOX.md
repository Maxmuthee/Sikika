# Running Sikika on the Africa's Talking Sandbox

This connects the **real telco path** (USSD + SMS) to Sikika, for free, with no
Communications Authority approval and no shortcode fees. Your `/ussd` and `/sms`
endpoints already speak Africa's Talking's exact format, so there is **no code to
change** — you only point AT at your server.

> Keep the local phone simulator (`/simulator`) as your failsafe demo — it needs
> no internet, no ngrok, and no AT. Use the sandbox as the "and here it is on a
> real gateway" proof.

---

## Prerequisites
- The app running locally (`uvicorn app.main:app --reload` → http://localhost:8000)
- A free [Africa's Talking](https://africastalking.com) account
- [ngrok](https://ngrok.com/download) (or any tunnel) to expose localhost publicly

---

## Step 1 — Get your sandbox API key
1. Sign up / log in at africastalking.com and open the **Sandbox** app (it's the default).
2. Go to **Settings → API Key**, generate a key, copy it.
3. Your username in sandbox is literally `sandbox`.

Put it in `.env`:
```
AT_USERNAME=sandbox
AT_API_KEY=<the sandbox key you copied>
```
(Leave `AT_API_KEY` blank and Sikika just logs SMS locally — the simulator still works.)

---

## Step 2 — Run the server
```bash
python scripts/init_db.py           # once, if you haven't seeded the DB
uvicorn app.main:app --reload       # serves on http://localhost:8000
```

## Step 3 — Expose it publicly
```bash
ngrok http 8000
```
Copy the HTTPS forwarding URL, e.g. `https://ab12-34-56.ngrok-free.app`.
That base URL + the path is what AT will call. Keep ngrok running.

---

## Step 4 — Point the USSD channel at Sikika
1. In the AT dashboard: **Sandbox → USSD → Create Channel**.
2. Request/keep a channel (you'll get a code like `*384*99#`).
3. Set the **Callback URL** to:
   ```
   https://<your-ngrok>.ngrok-free.app/ussd
   ```
4. Save.

That's it for USSD. AT will POST `sessionId`, `phoneNumber`, `serviceCode`, `text`
to `/ussd`, and Sikika replies with `CON …` / `END …` — exactly what AT expects.

---

## Step 5 — (Optional) wire SMS both ways
- **Outbound** (alerts + AI answers) already works once `AT_API_KEY` is set — Sikika
  sends via the AT SMS API. Restart uvicorn after editing `.env`.
- **Inbound** (citizen texts a question): **Sandbox → SMS → Inbox / Shortcodes**,
  create a shortcode or keyword, and set its **incoming-messages callback** to:
  ```
  https://<your-ngrok>.ngrok-free.app/sms
  ```
  AT posts `from`, `to`, `text` to `/sms`; Sikika answers and sends the reply back.

---

## Step 6 — Test it
1. In the AT dashboard: **Sandbox → Launch Simulator**.
2. Enter a phone number in international format, e.g. `+254711111111`, and connect.
3. **Dial your USSD code** (e.g. `*384*99#`) → you should see Sikika's language menu,
   then register / browse / vote through the real gateway.
4. **SMS**: send a text to your sandbox shortcode → Sikika replies (AI answer / alert).
   Outbound alerts you trigger (`scripts/notify.py <id>`) show in the simulator's inbox.

---

## Troubleshooting
- **USSD shows nothing / error** → the callback URL is wrong or ngrok died. Re-copy
  the current ngrok URL into the channel (it changes each restart on the free plan).
- **"Session ended" immediately** → check the uvicorn logs; a 500 in `/ussd` ends the
  session. The USSD log line prints the reply for each request.
- **SMS not sending** → confirm `AT_USERNAME=sandbox` and `AT_API_KEY` are set and you
  restarted uvicorn. Sandbox SMS appears in the simulator, not on a real handset.
- **Numbers** must be international format (`+2547…`).
- Free ngrok URLs change on every restart — update the AT callbacks when that happens.

---

## What's sandbox-only
- SMS/USSD are simulated (AT's Launch Simulator), not delivered to real SIM cards.
- Going to real phones = a **production** shortcode (paid, CA-approved). Nothing in the
  code changes for that — you swap the sandbox key/username for production ones.
