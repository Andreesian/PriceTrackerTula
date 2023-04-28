import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update, ForceReply
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TELEGRAM_API_KEY = "6130313049:AAEO-bM2-RzwwxU9K8H0oKstApDGid3xh8w"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define a function to fetch and parse the price
async def fetch_price(url: str, css_selector: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    price = soup.select_one(css_selector).text.strip()
    return price

# Define a function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! Send me a URL and CSS selector separated by a space."
    )

# Define a function to handle messages
async def parse_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        url, css_selector = update.message.text.split(" ", 1)
        price = await fetch_price(url, css_selector)
        await update.message.reply_text(f"The price is: {price}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main() -> None:
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, parse_price))

    application.run_polling()

if __name__ == "__main__":
    main()