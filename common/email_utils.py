import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from decouple import config


def send_set_password_email(receiver_email, user_name, setup_link):
    """
    Send password setup email to new user.
    
    Args:
        receiver_email: Email address of the recipient
        user_name: Full name of the user
        setup_link: Unique link for password setup
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    sender_email = config('EMAIL_HOST_USER')
    password = config('EMAIL_HOST_PASSWORD')
    
    # Create the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Set Up Your Account Password"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    
    # Email content (plain + HTML)
    text = f"""Hi {user_name},

Welcome to Accipere!

Your account has been created. Please set up your password by clicking the link below:

{setup_link}

This link will expire in 2 days.

If you didn't request this account, please ignore this email.

Best regards,
Accipere Team
"""
    
    html = f"""
<html>
<body>
    <p>Hi <b>{user_name}</b>,</p>
    <p>Welcome to <b>Accipere</b>!</p>
    <p>Your account has been created. Please set up your password by clicking the button below:</p>
    <p style="margin: 30px 0;">
        <a href="{setup_link}" 
           style="background-color: #4CAF50; color: white; padding: 14px 28px; 
                  text-decoration: none; border-radius: 4px; display: inline-block;">
            Set Up Password
        </a>
    </p>
    <p>Or copy and paste this link in your browser:</p>
    <p><a href="{setup_link}">{setup_link}</a></p>
    <p><small>This link will expire in 2 days.</small></p>
    <p>If you didn't request this account, please ignore this email.</p>
    <br>
    <p>Best regards,<br><b>Accipere Team</b></p>
</body>
</html>
"""
    
    # Attach both plain text and HTML
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    
    # Send email using Gmail SMTP
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"❌ Email Error: {e}")
        return False
