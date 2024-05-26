import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(attachment):
    port = 465
    password = "yfqg loqy mlna btbz"
    address = "camilocoding@gmail.com"

    # Create multipart message
    body = "Search results for a campground in Terre Et Mer in Tadoussac"

    message = MIMEMultipart()
    message["From"] = address
    message["To"] = address
    message["Subject"] = "Camping - Search Results"

    message.attach(MIMEText(body, "plain"))

    # Encode attachement
    filename = attachment
    with open(filename, "rb") as file:
        #Contenty-Type: Application/Octet-stream means that the file is binary data of unidentified type
        part = MIMEBase("application", "octet-stream")
        #set_payload() assigns the content to the instance of MIMEBase
        part.set_payload(file.read())

    # Encode attachment using ASCII characters
    encoders.encode_base64(part)
    #Content-Disposition: Attachment means that this is a file you need to download
    #Filename is added to let the browser know what name to use when the file is saved to disk
    part.add_header("Content-Disposition", f"attachment; filename= {filename}")

    # Add attachment to multipart email
    message.attach(part)
    message = message.as_string()

    # Creates a secure context using default safety paramters
    context = ssl.create_default_context()

    # Using with ensures that the server is closed after executing the block of code inside
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(address, password)
        server.sendmail(address, address, message)

