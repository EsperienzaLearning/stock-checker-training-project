
import requests
from bs4 import BeautifulSoup
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CURRYS_URL = "https://www.currys.co.uk/appliances/air-conditioners/portable-air-conditioners"

# Your email settings
EMAIL_SENDER = "darrenjsmith27@gmail.com"
EMAIL_RECEIVER = "darrenjsmith27@gmail.com"
EMAIL_PASSWORD = "USE_GITHUB_SECRET"

def check_stock():
    print("Fetching Currys page...")

    # Browser headers to avoid 403 Forbidden
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.currys.co.uk/",
    }

    try:
        response = requests.get(CURRYS_URL, headers=headers, timeout=10)
    except Exception as e:
        print(f"Request failed: {e}")
        return False, []

    if response.status_code != 200:
        print(f"Error fetching page: {response.status_code}")
        return False, []

    soup = BeautifulSoup(response.text, "html.parser")

    # Currys product tiles
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


