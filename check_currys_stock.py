from playwright.sync_api import sync_playwright
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CURRYS_URL = "https://www.currys.co.uk/appliances/air-conditioners/portable-air-conditioners"

EMAIL_SENDER = "your_email_here@gmail.com"
EMAIL_RECEIVER = "your_email_here@gmail.com"
EMAIL_PASSWORD = "USE_GITHUB_SECRET"

def check_stock():
    print("Launching browser...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Fetching Currys page...")
        page.goto(CURRYS_URL, timeout=60000)

        # Wait for product tiles to load
        page.wait_for_selector("div.product", timeout=30000)

        products = page.query_selector_all("div.product")

        in_stock_items = []

        for product in products:
            title = product.query_selector("h3")
            stock = product.query_selector("p.availability")

            title_text = title.inner_text().strip() if title else "Unknown product"
            stock_text = stock.inner_text().strip() if stock else "Unknown"

            if "in stock" in stock_text.lower() or "available" in stock_text.lower():
                in_stock_items.append(title_text)

        browser.close()

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
