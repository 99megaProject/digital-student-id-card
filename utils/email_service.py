import smtplib
from email.message import EmailMessage
import ssl
import os

from dotenv import load_dotenv


load_dotenv()  # Loads variables from .env into os.environ

password = os.getenv("EMAIL_PASSWORD")
sender_email = "sandeepxt99@gmail.com"

def send_email(subject: str, body: str, receiver_email: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 465):
    """
    Sends an email using the provided credentials and message details.

    Note: For security, it is highly recommended to use environment variables
    (e.g., os.environ.get('EMAIL_PASSWORD')) instead of hardcoding the password.

    Args:
        subject (str): The subject line of the email.
        body (str): The main content/body of the email.
        receiver_email (str): The recipient's email address.
        sender_email (str): The sender's email address (must match the login user).
        password (str): The sender's email password or application-specific password.
        smtp_server (str, optional): The SMTP server address. Defaults to "smtp.gmail.com".
        smtp_port (int, optional): The SMTP server port. Defaults to 465 (SSL).

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    # 1. Create the Email Message object
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(body)

    # 2. Add an optional SSL context for secure connection
    # Note: For port 465 (SMTPS), SSL context is typically required.
    context = ssl.create_default_context()

    try:
        # 3. Connect to the SMTP server and send the email
        # For port 465, use smtplib.SMTP_SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            # Login to the server
            server.login(sender_email, password)
            
            # Send the email
            server.send_message(msg)
            print(f"Successfully sent email to {receiver_email}")
            return True

    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP Authentication Failed. Check your username and password.")
        print("If using Gmail, ensure 'Less secure app access' is enabled or use an App Password.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

