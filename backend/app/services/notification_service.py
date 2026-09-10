"""Notification service for RM alerts.

Supports:
- SMTP email delivery (for production)
- Console logging fallback (for PoC)
- Daily digest of open alerts
- Immediate notification for critical alerts
"""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Alert, Farmer, Farm, RiskScore

logger = logging.getLogger("sarp.notifications")

# Email configuration from environment
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "sarp@sathapana.com.kh")
ENABLE_EMAIL = bool(SMTP_HOST and SMTP_USER)

# RM email mapping (in production this would come from HR system)
RM_EMAILS = {
    "Sovannara": "sovannara@sathapana.com.kh",
    "Dara": "dara@sathapana.com.kh",
    "Chantrea": "chantrea@sathapana.com.kh",
    "Bopha": "bopha@sathapana.com.kh",
    "Vannak": "vannak@sathapana.com.kh",
    "Srey Touch": "sreytouch@sathapana.com.kh",
    "Makara": "makara@sathapana.com.kh",
    "Rathana": "rathana@sathapana.com.kh",
    "Chamroeun": "chamroeun@sathapana.com.kh",
    "Kosal": "kosal@sathapana.com.kh",
}


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send an HTML email."""
    if not ENABLE_EMAIL:
        logger.info(f"[EMAIL SIMULATED] To: {to_email} | Subject: {subject}")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_critical_alert(alert: Alert, farmer: Farmer, farm: Farm, risk: RiskScore):
    """Send immediate notification for critical alerts."""
    rm_name = alert.assigned_to or "Unassigned"
    rm_email = RM_EMAILS.get(rm_name)

    subject = f"🔴 CRITICAL Alert: {alert.title} — {farmer.farmer_code}"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #ef4444;">🔴 Critical Alert: {alert.title}</h2>
        <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
            <tr><td style="padding: 8px; font-weight: bold;">Alert Code:</td><td>{alert.alert_code}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Farmer:</td><td>{farmer.farmer_code} — {farmer.name}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Province:</td><td>{farmer.province}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Farm:</td><td>{farm.farm_code} ({farm.area_hectares} ha)</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Risk Score:</td><td style="color: #ef4444; font-weight: bold;">{risk.risk_probability:.0%}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Risk Bucket:</td><td>{risk.risk_bucket}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Description:</td><td>{alert.description}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold;">Assigned To:</td><td>{rm_name}</td></tr>
        </table>
        <p style="margin-top: 20px;">
            <a href="http://localhost:5173/alerts" style="background: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View Alert →</a>
        </p>
    </body>
    </html>
    """

    if rm_email:
        send_email(rm_email, subject, html_body)
    else:
        logger.warning(f"No email for RM {rm_name}, alert notification skipped")


def send_daily_digest(rm_name: str, alerts: list[Alert], farmers: dict):
    """Send daily digest of open alerts to an RM."""
    rm_email = RM_EMAILS.get(rm_name)
    if not rm_email and ENABLE_EMAIL:
        return

    if not alerts:
        return

    # Build alert rows
    rows = ""
    for a in alerts:
        f = farmers.get(a.farm_id, {})
        severity_color = {
            "CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#f59e0b", "LOW": "#22c55e",
        }.get(a.severity, "#6b7280")
        rows += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{a.alert_code}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{f.get('farmer_code', 'N/A')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; color: {severity_color}; font-weight: bold;">{a.severity}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{a.title}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{a.status}</td>
        </tr>"""

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>📋 Daily Alert Digest — {rm_name}</h2>
        <p>You have <strong>{len(alerts)}</strong> open alerts requiring attention.</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 800px;">
            <thead>
                <tr style="background: #f3f4f6;">
                    <th style="padding: 8px; text-align: left;">Alert</th>
                    <th style="padding: 8px; text-align: left;">Farmer</th>
                    <th style="padding: 8px; text-align: left;">Severity</th>
                    <th style="padding: 8px; text-align: left;">Title</th>
                    <th style="padding: 8px; text-align: left;">Status</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <p style="margin-top: 20px;">
            <a href="http://localhost:5173/alerts" style="background: #4f8ff7; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View All Alerts →</a>
        </p>
    </body>
    </html>
    """

    subject = f"📋 SARP Daily Digest: {len(alerts)} open alerts — {datetime.now().strftime('%Y-%m-%d')}"

    if ENABLE_EMAIL:
        send_email(rm_email, subject, html_body)
    else:
        logger.info(f"[DIGEST SIMULATED] RM: {rm_name} | Alerts: {len(alerts)}")


def send_alert_notifications(db: Session):
    """Check for unnotified alerts and send notifications."""
    from datetime import timedelta

    # Get open critical and high alerts
    critical_alerts = (
        db.query(Alert)
        .filter(Alert.status == "open", Alert.severity == "CRITICAL")
        .all()
    )

    # Send immediate notifications for critical alerts
    for alert in critical_alerts:
        farmer = db.query(Farmer).join(Farm, Farm.farmer_id == Farmer.id).filter(Farm.id == alert.farm_id).first()
        farm = db.query(Farm).filter(Farm.id == alert.farm_id).first()
        risk = (
            db.query(RiskScore)
            .filter(RiskScore.farm_id == alert.farm_id)
            .order_by(RiskScore.scoring_date.desc())
            .first()
        )
        if farmer and farm:
            send_critical_alert(alert, farmer, farm, risk)

    # Build daily digest per RM
    open_alerts = (
        db.query(Alert)
        .filter(Alert.status.in_(["open", "acknowledged"]))
        .all()
    )

    # Group by RM
    rm_alerts = {}
    farm_ids = set()
    for a in open_alerts:
        rm = a.assigned_to or "Unassigned"
        rm_alerts.setdefault(rm, []).append(a)
        farm_ids.add(a.farm_id)

    # Fetch farmer info
    farms = db.query(Farm).filter(Farm.id.in_(farm_ids)).all()
    farmer_map = {}
    for farm in farms:
        farmer = db.query(Farmer).filter(Farmer.id == farm.farmer_id).first()
        farmer_map[farm.id] = {
            "farmer_code": farmer.farmer_code if farmer else "N/A",
            "name": farmer.name if farmer else "N/A",
        }

    # Send digests
    for rm_name, alerts in rm_alerts.items():
        send_daily_digest(rm_name, alerts, farmer_map)
