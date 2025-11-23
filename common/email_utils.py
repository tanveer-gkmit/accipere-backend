import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config


import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config


def _send_email(receiver_email, subject, text_content, html_content):
    """
    Send email using SendGrid SMTP.
    """
    # The FROM address (must be verified in SendGrid)
    sender_email = config('EMAIL_HOST_USER')
    
    # SendGrid API key
    sendgrid_api_key = config('EMAIL_HOST_PASSWORD')
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    
    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        context = ssl.create_default_context()
        
        with smtplib.SMTP("smtp.sendgrid.net", 587, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            
            # CRITICAL FIX: Use "apikey" as username, not the email address
            server.login("apikey", sendgrid_api_key)
            
            server.send_message(msg)
        
        print(f"✅ Email sent successfully to {receiver_email}")
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Email Error: {e}")
        print(traceback.format_exc())
        return False



def _create_email_template(title, greeting, message, link, button_text, gradient_colors, info_box):
    """
    Create a styled HTML email template.
    """
    start_color, end_color = gradient_colors
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 30px 40px; background: linear-gradient(135deg, {start_color} 0%, {end_color} 100%); border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600; text-align: center;">
                                {title}
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px; line-height: 1.6;">
                                {greeting}
                            </p>
                            
                            {message}
                            
                            <!-- Button -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td align="center" style="padding: 0 0 30px 0;">
                                        <a href="{link}" 
                                           style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, {start_color} 0%, {end_color} 100%); 
                                                  color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; 
                                                  font-weight: 600; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);">
                                            {button_text}
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0 0 10px 0; color: #777777; font-size: 13px; line-height: 1.6;">
                                Or copy and paste this link in your browser:
                            </p>
                            <p style="margin: 0 0 30px 0; word-break: break-all;">
                                <a href="{link}" style="color: {start_color}; text-decoration: none; font-size: 13px;">
                                    {link}
                                </a>
                            </p>
                            
                            <!-- Info/Warning Box -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: {info_box['bg_color']}; border-radius: 6px; border-left: 4px solid {info_box['border_color']};">
                                <tr>
                                    <td style="padding: 15px 20px;">
                                        <p style="margin: 0; color: {info_box['text_color']}; font-size: 13px; line-height: 1.5;">
                                            {info_box['content']}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f9fa; border-radius: 0 0 8px 8px; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 10px 0; color: #555555; font-size: 14px;">
                                Best regards,<br>
                                <strong>The Accipere Team</strong>
                            </p>
                            <p style="margin: 0; color: #999999; font-size: 12px;">
                                © 2024 Accipere. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


def send_set_password_email(receiver_email, user_name, setup_link):
    """Send password setup email to new user."""
    subject = "Welcome to Accipere - Set Up Your Account"
    
    text = f"""Hi {user_name},

Welcome to Accipere!

Your account has been created. Please set up your password by clicking the link below:

{setup_link}

This link will expire in 2 days.

If you didn't request this account, please ignore this email.

Best regards,
Accipere Team
"""
    
    message = """
<p style="margin: 0 0 20px 0; color: #555555; font-size: 15px; line-height: 1.6;">
    Your account has been successfully created! We're excited to have you on board.
</p>

<p style="margin: 0 0 30px 0; color: #555555; font-size: 15px; line-height: 1.6;">
    To get started, please set up your password by clicking the button below:
</p>
"""
    
    info_box = {
        'bg_color': '#f8f9fa',
        'border_color': '#667eea',
        'text_color': '#555555',
        'content': '⏰ <strong>Note:</strong> This link will expire in 2 days for security reasons.<br><br>If you didn\'t request this account, please ignore this email.'
    }
    
    html = _create_email_template(
        title="Welcome to Accipere",
        greeting=f"Hi <strong>{user_name}</strong>,",
        message=message,
        link=setup_link,
        button_text="Set Up Your Password",
        gradient_colors=('#667eea', '#764ba2'),
        info_box=info_box
    )
    
    return _send_email(receiver_email, subject, text, html)


def send_reset_password_email(receiver_email, user_name, reset_link):
    """Send password reset email to existing user."""
    subject = "Reset Your Accipere Password"
    
    text = f"""Hi {user_name},

A password reset has been requested for your Accipere account.

Please reset your password by clicking the link below:

{reset_link}

This link will expire in 2 days.

If you didn't request this password reset, please contact your administrator immediately.

Best regards,
Accipere Team
"""
    
    message = """
<p style="margin: 0 0 20px 0; color: #555555; font-size: 15px; line-height: 1.6;">
    A password reset has been requested for your Accipere account by an administrator.
</p>

<p style="margin: 0 0 30px 0; color: #555555; font-size: 15px; line-height: 1.6;">
    To reset your password, please click the button below:
</p>
"""
    
    info_box = {
        'bg_color': '#fff3cd',
        'border_color': '#ffc107',
        'text_color': '#856404',
        'content': '⚠️ <strong>Security Notice:</strong><br><br>This link will expire in 2 days. If you didn\'t request this password reset, please contact your administrator immediately.'
    }
    
    html = _create_email_template(
        title="Password Reset Request",
        greeting=f"Hi <strong>{user_name}</strong>,",
        message=message,
        link=reset_link,
        button_text="Reset Your Password",
        gradient_colors=('#f093fb', '#f5576c'),
        info_box=info_box
    )
    
    return _send_email(receiver_email, subject, text, html)
