"""
Email Service for Colatrack Platform.

Sends welcome emails to newly created technician accounts
with their login credentials.
Uses Python's built-in smtplib (no extra dependencies).
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.models.incident import Incident

logger = logging.getLogger(__name__)


def send_welcome_email(to_email: str, username: str, password: str) -> bool:
    """
    Send a welcome email to a newly created technician with their credentials.
    
    Args:
        to_email: Recipient email address
        username: The technician's username
        password: The plain-text default password
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured — skipping welcome email for %s", username)
        return False

    subject = "Bienvenue sur Colatrack — Vos identifiants de connexion"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f1f5f9; margin: 0; padding: 0; }}
            .container {{ max-width: 560px; margin: 40px auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
            .header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 32px 40px; text-align: center; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
            .header p {{ color: #94a3b8; margin: 8px 0 0; font-size: 14px; }}
            .body {{ padding: 40px; }}
            .greeting {{ font-size: 18px; color: #1e293b; font-weight: 600; margin-bottom: 16px; }}
            .text {{ color: #475569; font-size: 14px; line-height: 1.7; margin-bottom: 24px; }}
            .credentials {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin: 24px 0; }}
            .credentials .label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; font-weight: 600; margin-bottom: 4px; }}
            .credentials .value {{ font-size: 16px; color: #0f172a; font-weight: 700; font-family: 'Courier New', monospace; margin-bottom: 16px; }}
            .credentials .value:last-child {{ margin-bottom: 0; }}
            .btn {{ display: inline-block; background: #059669; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 10px; font-weight: 600; font-size: 14px; margin: 8px 0; }}
            .warning {{ background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 16px; margin: 24px 0; }}
            .warning p {{ color: #92400e; font-size: 13px; margin: 0; line-height: 1.6; }}
            .footer {{ padding: 24px 40px; background: #f8fafc; border-top: 1px solid #e2e8f0; text-align: center; }}
            .footer p {{ color: #94a3b8; font-size: 12px; margin: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Colatrack</h1>
                <p>Plateforme de Pilotage Industriel</p>
            </div>
            <div class="body">
                <p class="greeting">Bonjour {username},</p>
                <p class="text">
                    Votre compte technicien a été créé sur la plateforme Colatrack. 
                    Vous pouvez dès maintenant vous connecter avec les identifiants ci-dessous.
                </p>
                
                <div class="credentials">
                    <div class="label">Nom d'utilisateur</div>
                    <div class="value">{username}</div>
                    <div class="label">Mot de passe</div>
                    <div class="value">{password}</div>
                </div>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{settings.PLATFORM_URL}" class="btn">Se connecter à Colatrack</a>
                </div>
                
                <div class="warning">
                    <p>
                        🔒 <strong>Important :</strong> Pour des raisons de sécurité, veuillez changer 
                        votre mot de passe dès votre première connexion en vous rendant dans 
                        <strong>Mon Compte → Sécurité et Accès</strong>.
                    </p>
                </div>
            </div>
            <div class="footer">
                <p>Cet email a été envoyé automatiquement par la plateforme Colatrack.</p>
                <p>Ne partagez jamais vos identifiants avec d'autres personnes.</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
        msg["To"] = to_email

        # Plain-text fallback
        text_body = (
            f"Bonjour {username},\n\n"
            f"Votre compte technicien a été créé sur Colatrack.\n\n"
            f"Nom d'utilisateur : {username}\n"
            f"Mot de passe : {password}\n\n"
            f"Connectez-vous ici : {settings.PLATFORM_URL}\n\n"
            f"Important : Changez votre mot de passe dès la première connexion "
            f"dans Mon Compte → Sécurité et Accès.\n"
        )

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(
                settings.SMTP_FROM_EMAIL or settings.SMTP_USER,
                to_email,
                msg.as_string()
            )

        logger.info("Welcome email sent successfully to %s", to_email)
        return True

    except Exception as e:
        logger.error("Failed to send welcome email to %s: %s", to_email, str(e))
        return False


def send_incident_assignment_email(to_email: str, username: str, incident: Incident) -> bool:
    """
    Send an email notifying a technician that an incident has been assigned to them.
    
    Args:
        to_email: Recipient email address
        username: The technician's username
        incident: The Incident model instance
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured — skipping incident email for %s", username)
        return False

    is_critical = incident.criticite in ["Critique", "Élevé"]
    
    # Priority colors
    badge_bg = "#fee2e2" if is_critical else ("#fef3c7" if incident.criticite == "Moyen" else "#f1f5f9")
    badge_text = "#991b1b" if is_critical else ("#92400e" if incident.criticite == "Moyen" else "#475569")
    
    subject_prefix = "🚨 URGENT: " if is_critical else "📝 NOUVEL: "
    subject = f"{subject_prefix}Incident Assigné - {incident.equipement} ({incident.ligne})"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f1f5f9; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
            .header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 32px 40px; text-align: center; border-bottom: 4px solid {'#ef4444' if is_critical else '#3b82f6'}; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
            .header p {{ color: #94a3b8; margin: 8px 0 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
            .body {{ padding: 40px; }}
            .greeting {{ font-size: 18px; color: #1e293b; font-weight: 600; margin-bottom: 24px; }}
            
            table.details {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; background: #f8fafc; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }}
            table.details th {{ padding: 14px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; width: 35%; }}
            table.details td {{ padding: 14px 16px; border-bottom: 1px solid #e2e8f0; font-size: 14px; color: #0f172a; font-weight: 500; }}
            table.details tr:last-child th, table.details tr:last-child td {{ border-bottom: none; }}
            
            .badge {{ display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 13px; font-weight: 600; background: {badge_bg}; color: {badge_text}; }}
            
            .description-box {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; border-left: 4px solid {'#ef4444' if is_critical else '#3b82f6'}; margin-top: 8px; }}
            .description-box .label {{ font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 600; margin-bottom: 8px; }}
            .description-box .text {{ color: #334155; font-size: 14px; line-height: 1.6; margin: 0; white-space: pre-wrap; }}
            
            .btn-container {{ text-align: center; margin: 32px 0 16px; }}
            .btn {{ display: inline-block; background: #0f172a; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 10px; font-weight: 600; font-size: 14px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
            
            .footer {{ padding: 24px 40px; background: #f8fafc; border-top: 1px solid #e2e8f0; text-align: center; }}
            .footer p {{ color: #94a3b8; font-size: 12px; margin: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Colatrack</h1>
                <p>Assignation d'Incident</p>
            </div>
            <div class="body">
                <p class="greeting">Bonjour {username},</p>
                
                <p style="color: #475569; font-size: 15px; line-height: 1.6; margin-bottom: 24px;">
                    Un nouvel incident vous a été assigné sur la plateforme Colatrack. 
                    Veuillez en prendre connaissance et intervenir dans les délais impartis.
                </p>
                
                <table class="details">
                    <tr>
                        <th>Ligne</th>
                        <td>{incident.ligne}</td>
                    </tr>
                    <tr>
                        <th>Équipement</th>
                        <td>{incident.equipement}</td>
                    </tr>
                    <tr>
                        <th>Type d'incident</th>
                        <td>{incident.type_incident}</td>
                    </tr>
                    <tr>
                        <th>Criticité</th>
                        <td><span class="badge">{incident.criticite}</span></td>
                    </tr>
                    <tr>
                        <th>Deadline</th>
                        <td>{incident.deadline.strftime("%d/%m/%Y")}</td>
                    </tr>
                </table>
                
                <div class="description-box">
                    <div class="label">Description du problème</div>
                    <p class="text">{incident.description_probleme}</p>
                </div>
                
                <div class="btn-container">
                    <a href="{settings.PLATFORM_URL}/dashboard/incidents" class="btn">Voir les incidents sur Colatrack</a>
                </div>
            </div>
            <div class="footer">
                <p>Cet email a été envoyé automatiquement par la plateforme Colatrack.</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
        msg["To"] = to_email

        # Plain-text fallback
        text_body = (
            f"Bonjour {username},\n\n"
            f"Un nouvel incident vous a été assigné sur Colatrack.\n\n"
            f"Détails de l'incident :\n"
            f"- Ligne : {incident.ligne}\n"
            f"- Équipement : {incident.equipement}\n"
            f"- Type : {incident.type_incident}\n"
            f"- Criticité : {incident.criticite}\n"
            f"- Deadline : {incident.deadline.strftime('%d/%m/%Y')}\n\n"
            f"Description :\n{incident.description_probleme}\n\n"
            f"Veuillez vous connecter pour le prendre en charge : {settings.PLATFORM_URL}/dashboard/incidents"
        )

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(
                settings.SMTP_FROM_EMAIL or settings.SMTP_USER,
                to_email,
                msg.as_string()
            )

        logger.info("Incident assignment email sent successfully to %s", to_email)
        return True

    except Exception as e:
        logger.error("Failed to send incident email to %s: %s", to_email, str(e))
        return False
