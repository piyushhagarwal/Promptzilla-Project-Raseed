import smtplib
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def send_invoice_email(
    smtp_server: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    sender_email: str,
    recipient_email: str,
    invoice_image_data: bytes,
    google_wallet_link: str
):
    """
    Sends a beautiful HTML invoice email with an in-memory image and a Google Wallet link.

    Args:
        smtp_server (str): The SMTP server address.
        smtp_port (int): The SMTP server port.
        smtp_user (str): The username for SMTP authentication.
        smtp_password (str): The password for SMTP authentication.
        sender_email (str): The email address of the sender.
        recipient_email (str): The email address of the recipient.
        invoice_image_data (bytes): The image data for the invoice as a byte string.
        google_wallet_link (str): The URL for the 'Add to Google Wallet' button.
    """
    try:
        # --- 1. Read the HTML Template ---
        try:
            # Assumes the updated 'mail.html' is in the same directory.
            with open('./mail.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            print("Error: 'mail.html' not found. Make sure the HTML template file is in the same directory.")
            return

        # --- 2. Personalize the HTML Content ---
        # Replace the placeholder for the wallet link.
        # The image placeholder is handled by the CID embedding below.
        html_content = html_content.replace('{YOUR_WALLET_LINK_HERE}', google_wallet_link)

        # --- 3. Create the Email Message ---
        msg = MIMEMultipart('related')
        msg['Subject'] = "Your Google Wallet Pass is Ready to be added -- Project Raseed"
        msg['From'] = f"Project Raseed"
        msg['To'] = recipient_email

        # Attach the HTML part
        msg.attach(MIMEText(html_content, 'html'))

        # --- 4. Embed the In-Memory Image ---
        # This ensures the image displays in the email without being blocked.
        # The 'cid' (Content-ID) must match the src in the HTML's <img> tag.
        img = MIMEImage(invoice_image_data)
        img.add_header('Content-ID', '<invoiceimage>')
        img.add_header('Content-Disposition', 'inline', filename="invoice_item.png")
        msg.attach(img)

        # --- 5. Connect to the SMTP Server and Send ---
        print(f"Connecting to SMTP server at {smtp_server}:{smtp_port}...")
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            print("Logging in...")
            server.login(smtp_user, smtp_password)
            print("Sending email...")
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Email sent successfully to {recipient_email}!")

    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Check your username and password.")
    except smtplib.SMTPServerDisconnected:
        print("SMTP Server Disconnected: The server unexpectedly disconnected.")
    except smtplib.SMTPException as e:
        print(f"An SMTP error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    # --- CONFIGURATION ---

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    SMTP_USER = ""
    SMTP_PASSWORD = "" # Use an App Password for Gmail

    SENDER_EMAIL = "yarndev.barclays@gmail.com"
    RECIPIENT_EMAIL = "mihirdesh23@gmail.com"

    # --- Create a dummy image IN MEMORY for testing ---

    invoice_image_bytes = None
    try:
        from PIL import Image, ImageDraw, ImageFont
        # Create an image with variable dimensions
        img = Image.new('RGB', (800, 250), color = (76, 175, 80)) # Green background
        d = ImageDraw.Draw(img)
        try:
            # Use a common font
            font = ImageFont.truetype("arial.ttf", 30)
        except IOError:
            font = ImageFont.load_default()
        d.text((50, 100), "Your Product / Service Image", fill=(255, 255, 255), font=font)
        
        # Save the image to an in-memory bytes buffer
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        invoice_image_bytes = byte_arr.getvalue()
        print("Created a placeholder image in memory.")

    except ImportError:
        print("Pillow library not found. Cannot create placeholder image.")
        print("To run this example, install it: pip install Pillow")
    except Exception as e:
        print(f"Could not create placeholder image: {e}")


    # --- Call the function to send the email ---
    # Only proceed if the image data was successfully created.
    if invoice_image_bytes:
        send_invoice_email(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            smtp_user=SMTP_USER,
            smtp_password=SMTP_PASSWORD,
            sender_email=SENDER_EMAIL,
            recipient_email=RECIPIENT_EMAIL,
            invoice_image_data=invoice_image_bytes,
            google_wallet_link=WALLET_LINK
        )

