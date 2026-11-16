# BlueDesk IT website

Managed IT support website for BlueDesk IT (Nairobi, Kenya).

```
index.html          the website (raw HTML)
app.py              Flask server: serves the site and sends contact-form emails
render.yaml         Render deployment settings
streamlit_app.py    view-only preview in Streamlit
php/                PHP + PHPMailer version, for cPanel hosting
.env.example        list of settings (copy to .env locally; never commit .env)
```

## Put it on GitHub
```bash
cd bluedesk-it
git init
git add .
git commit -m "BlueDesk IT website"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bluedesk-it.git
git push -u origin main
```
Create the empty repository on github.com first (private is fine). Passwords are never in the repo: `.gitignore` excludes `.env` and `php/config.php`.

## Render (live site with working form)
1. Render dashboard > New > Web Service > connect the GitHub repo. It reads `render.yaml`.
2. Add the environment variables when asked.
3. Email: Render's free plan blocks SMTP ports (25, 465, 587). Choose one:
   - Free plan: create a Resend account, verify bluedesk.co.ke (add the DNS records it shows), set `RESEND_API_KEY`. Mail is sent from info@bluedesk.co.ke over HTTPS.
   - Paid plan: set `SMTP_PASS` and keep the SMTP settings. Mail goes through your mailbox directly.
4. Add the custom domain under Settings > Custom Domains.
Free web services sleep when idle, so the first visit can take about 30 seconds to wake. A paid plan avoids this.

## Streamlit (preview only)
share.streamlit.io > New app > pick the repo, branch `main`, main file `streamlit_app.py`. It renders the page, but the form does not send mail there.

## cPanel / PHP hosting (simplest for SMTP)
Upload `index.html` and the contents of `php/` into `public_html`. Rename `config.example.php` to `config.php` and set the mailbox password. Plain SMTP works there with no extra service.

## Before going live
- Replace the WhatsApp placeholder `254700000000` in `index.html`.
- Add SPF, DKIM and DMARC DNS records for bluedesk.co.ke so mail reaches inboxes.
