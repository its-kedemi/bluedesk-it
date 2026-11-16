"""BlueDesk IT: serves the website and handles the contact form.

Runs on Render (or any Python host). Secrets come from environment variables, never from the repo.
Mail is sent by SMTP, or by the Resend HTTP API if RESEND_API_KEY is set.
Render's free plan blocks SMTP ports, so on the free plan use RESEND_API_KEY.
"""
import json
import os
import re
import smtplib
import time
import urllib.request
from email.message import EmailMessage

from flask import Flask, redirect, request, send_from_directory

ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=None)

SMTP_HOST = os.getenv("SMTP_HOST", "mail.bluedesk.co.ke")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "info@bluedesk.co.ke")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "info@bluedesk.co.ke")
TO_EMAIL = os.getenv("TO_EMAIL", "info@bluedesk.co.ke")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
AUTO_REPLY = os.getenv("AUTO_REPLY", "1") == "1"

_last_seen = {}  # visitor IP -> time of last submission


def clean(value, limit):
    return re.sub(r"[\r\n]+", " ", (value or "")).strip()[:limit]


def send_mail(to, subject, body, from_name, reply_to=None):
    sender = f"{from_name} <{FROM_EMAIL}>"
    if RESEND_API_KEY:
        payload = {"from": sender, "to": [to], "subject": subject, "text": body}
        if reply_to:
            payload["reply_to"] = reply_to
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=15).read()
        return
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = sender, to, subject
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)
    if SMTP_PORT == 465:
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15)
    else:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
        server.starttls()
    with server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")


@app.get("/healthz")
def health():
    return "ok"


@app.post("/send")
@app.post("/send.php")
def send():
    if request.form.get("website"):  # hidden spam-trap field
        return redirect("/?sent=1#contact")

    ip = (request.headers.get("X-Forwarded-For", request.remote_addr) or "").split(",")[0].strip()
    now = time.time()
    if now - _last_seen.get(ip, 0) < 30:
        return redirect("/?sent=0#contact")
    _last_seen[ip] = now

    f = request.form
    name, business = clean(f.get("name"), 100), clean(f.get("business"), 120)
    email, phone = clean(f.get("email"), 150), clean(f.get("phone"), 30)
    size, plan = clean(f.get("size"), 40), clean(f.get("plan"), 40)
    message = (f.get("message") or "").strip()[:2000]

    if not name or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return redirect("/?sent=0#contact")

    body = (
        "New website enquiry\n\n"
        f"Name: {name}\nBusiness: {business}\nEmail: {email}\nPhone: {phone}\n"
        f"Team size: {size}\nPlan: {plan}\n\nMessage:\n{message}\n"
    )
    try:
        subject = f"Free IT check request from {name}" + (f" ({business})" if business else "")
        send_mail(TO_EMAIL, subject, body, "BlueDesk IT Website", reply_to=email)
        if AUTO_REPLY:
            send_mail(
                email,
                "We received your request – BlueDesk IT",
                f"Hi {name},\n\nThank you for contacting BlueDesk IT. We've received your request for a "
                "free IT health check and will reply within one working day.\n\nBlueDesk IT\ninfo@bluedesk.co.ke\n",
                "BlueDesk IT",
            )
    except Exception as exc:  # log the cause, show the visitor a friendly message
        app.logger.error("Mail error: %s", exc)
        return redirect("/?sent=0#contact")
    return redirect("/?sent=1#contact")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8002")), debug=False)
