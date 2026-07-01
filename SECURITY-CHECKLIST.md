# Pre-Launch Security & Privacy Checklist

Run this before every launch. ~30 minutes. The git pre-push hook auto-checks the
items marked **[auto]**; the rest are on you. Tick a box only after you've *verified*
it, not after you've *enabled* it.

> Baseline, not enterprise compliance. Storing health, financial, or other regulated
> data? You need a real audit on top of this.

---

## 1. Protect yourself legally (~10 min)
- [ ] Real privacy policy is live (Termly / PrivacyPolicies.com is fine to generate)
- [ ] You know exactly where user data lives (DB region, host region, every 3rd party touching it)
- [ ] Nothing dodgy: no selling data, no exporting to personal email, no plaintext passwords

## 2. Lock down the database
- [ ] **[auto]** No `.env` or secrets committed to git
- [ ] RLS enabled on every table with user data **and tested as a different user**
      (enabling RLS without testing it is worse than nothing — false confidence)
- [ ] Server-side validation on **every** form that writes to the DB
      (Zod on the client is UX, not security — attackers hit your API directly)
- [ ] Error messages are generic ("User not found"), full errors logged server-side only
- [ ] **[auto]** No stack traces / raw DB errors returned to the client

## 3. Test the auth failure cases (~10 min)
- [ ] Wrong password 5x in a row → locks / throttles, generic error (doesn't confirm email exists)
- [ ] Password reset for a non-existent email → doesn't reveal whether it's registered
- [ ] Email verification link clicked twice → handled gracefully, doesn't break the flow
- [ ] Signup with an already-registered email → doesn't leak that the user exists

## 4. Run the AI security prompts (~8 min)
Paste into Claude Code / Cursor against your app:
- [ ] *"Review my app as a security specialist — strong security headers and baseline posture."*
- [ ] *"Review my app against OWASP standards and highlight vulnerabilities."*
- [ ] *"Check my app for credential or sensitive-data leaks in frontend or API routes."*
- [ ] *"Ensure no API keys are exposed in frontend code or network calls."*

## 5. Environment variables & keys
- [ ] **[auto]** No secret keys (service_role, `sk_live`, `sk-ant`, OpenAI/Anthropic) in frontend code
- [ ] **[auto]** No secret behind a public prefix (`NEXT_PUBLIC_*`, `VITE_*`, `REACT_APP_*`)
- [ ] Public keys (Supabase anon, Stripe publishable) are fine in the frontend — confirmed these are public
- [ ] Secret keys live in server env / Edge Function Secrets / Vercel env vars only
- [ ] Any key that *might* have leaked is regenerated **now** (public repos get scraped in minutes)

## 6. Protect your infrastructure (protects your wallet)
- [ ] Rate limits on every endpoint hitting a paid API (OpenAI, Anthropic, Stripe, Resend)
- [ ] Hard daily spend caps set in the OpenAI/Anthropic dashboards
- [ ] Billing alerts at ~50% of the cap (catch a spike before the morning bill)
- [ ] CAPTCHA on public forms (Cloudflare Turnstile, free) — contact, signup, waitlist
- [ ] **[auto]** CORS restricted to your real domains (no `*`, no `AllowAnyOrigin()`)

## 7. Final gate
- [ ] Built-in scanner (Cursor / Claude Code / Lovable) run — **zero** warnings shipped
- [ ] (Optional, recommended) deep secret scan over git history: `gitleaks detect`

---

*Adapted from the 30-minute pre-launch checklist (Reddit dev base + agency layer).*
*The pre-push hook in this repo enforces the **[auto]** items and reminds you of the rest.*
