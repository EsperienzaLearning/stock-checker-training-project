import requests
from bs4 import BeautifulSoup
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CURRYS_URL = "https://www.currys.co.uk/appliances/air-conditioners/portable-air-conditioners"

# Your email settings
EMAIL_SENDER = "your_email_here@gmail.com"
EMAIL_RECEIVER = "your_email_here@gmail.com"
EMAIL_PASSWORD = "USE_GITHUB_SECRET"

def check_stock():
    print("Fetching Currys page...")
    response = requests.get(CURRYS_URL, timeout=10)

    if response.status_code != 200:
        print(f"Error fetching page: {response.status_code}")
        return False, []

    soup = BeautifulSoup(response.text, "html.parser")

    # Currys product tiles use <div class="product"> or similar
    products = soup.find_all("div", class_="product")

    in_stock_items = []

    for product in products:
        title_tag = product.find("h3")
        stock_tag = product.find("p", class_="availability")

        title = title_tag.text.strip() if title_tag else "Unknown product"
        stock = stock_tag.text.strip() if stock_tag else "Unknown"

        # Basic stock check
        if "in stock" in stock.lower() or "available" in stock.lower():
            in_stock_items.append(title)

    return len(in_stock_items) > 0, in_stock_items



def send_email(stock_items):
    subject = "Currys Air Conditioner Stock Alert"
    body = "The following portable air conditioners are in stock:\n\n"
    body += "\n".join(stock_items)

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

    print("Email sent!")


if __name__ == "__main__":
    stock_found, items = check_stock()

    if stock_found:
        print("Stock found!")
        print(items)
        send_email(items)
    else:
        print("No stock found.")
