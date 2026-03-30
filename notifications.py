"""notifications.py — SMTP email alerts"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


def send_alert(recipient: str, coin_id: str, change_pct: float,
               current_price: float, smtp_host: str = "smtp.gmail.com",
               smtp_port: int = 587, sender: str = "", password: str = "") -> tuple:
    if not recipient or "@" not in recipient:
        return False, "Invalid email."
    if not sender or not password:
        return False, "SMTP credentials not configured."

    direction = "dropped" if change_pct < 0 else "rose"
    subject   = f"[CryptoManager] {coin_id.upper()} {direction} {abs(change_pct):.1f}%"
    clr = "#DC2626" if change_pct < 0 else "#16A34A"
    html = f"""<div style="font-family:sans-serif;max-width:480px;margin:auto;background:#fff;
                border-radius:12px;overflow:hidden;border:1px solid #e5e7eb;">
      <div style="background:#0F766E;padding:20px 24px;">
        <h2 style="color:#fff;margin:0;font-size:18px;">Portfolio Alert</h2>
      </div>
      <div style="padding:24px;">
        <p style="margin:0 0 16px;color:#374151;">
          <strong>{coin_id.upper()}</strong> has {direction} significantly.
        </p>
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          <tr style="background:#f9fafb;"><td style="padding:10px;color:#6b7280;">Asset</td>
              <td style="padding:10px;font-weight:600;">{coin_id.upper()}</td></tr>
          <tr><td style="padding:10px;color:#6b7280;">Change</td>
              <td style="padding:10px;color:{clr};font-weight:700;">{change_pct:+.2f}%</td></tr>
          <tr style="background:#f9fafb;"><td style="padding:10px;color:#6b7280;">Price</td>
              <td style="padding:10px;font-weight:600;">${current_price:,.4g}</td></tr>
          <tr><td style="padding:10px;color:#6b7280;">Time</td>
              <td style="padding:10px;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</td></tr>
        </table>
        <p style="margin:16px 0 0;font-size:12px;color:#9ca3af;">
          CryptoPortfolio Manager — automated alert
        </p>
      </div>
    </div>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = sender
    msg["To"]      = recipient
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as s:
            s.starttls()
            s.login(sender, password)
            s.sendmail(sender, recipient, msg.as_string())
        return True, f"Alert sent to {recipient}."
    except Exception as e:
        return False, f"Send failed: {e}"