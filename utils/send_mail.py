import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
def render_template(template_name, **kwargs):
    # Set the correct path to the 'templates' directory
    base_dir = os.path.dirname(__file__)  # Directory where 'send_email.py' is located
    template_dir = os.path.join(base_dir, 'templates')  # Path to 'templates' directory

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_name)
    return template.render(**kwargs)

def send_email(subject, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password, template_name, **template_vars):
    html_content = render_template(template_name, **template_vars)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    part1 = MIMEText(html_content, 'html')
    msg.attach(part1)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Error: {e}")

# # Usage example
# send_email(
#     subject="Test Email",
#     body="This is a test email from Python.",
#     to_email="joshikommaraju@gmail.com",
#     from_email="connect@uptp.com",
#     smtp_server="smtp.gmail.com",
#     smtp_port=587,
#     smtp_user="hideoutprotocol@gmail.com",
#     smtp_password="bdbp opkn heyw ypaa",
#     template_name="example_template.html",
#     name="John Doe"
# )
