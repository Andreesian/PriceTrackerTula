from urllib.parse import urlparse

def get_domain_name(url):
    try:
        parsed_url = urlparse(url)
        domain = f"{parsed_url.netloc}"
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception as e:
        print(f"Error: {e}")
        return None

import logging
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationHandlerStop,
    CallbackQueryHandler,
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TELEGRAM_API_KEY = "6130313049:AAEO-bM2-RzwwxU9K8H0oKstApDGid3xh8w"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Set up Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

search_css_selectors = {
    "dns-shop.ru": ""
}

price_css_selectors = {
    "dns-shop.ru": ".product-buy__price"
}

#state
state = {
    "START" : False,
    "HELP" : False,
    "WANT_PRICE" : False
}

# Define a function to fetch and parse the price
async def fetch_price(url: str, css_selector: str) -> str:
    driver.get(url)
    element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    price = element.text.strip()
    return price

# Define a function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data="1")],
        [InlineKeyboardButton("Option 2", callback_data="2")],
        [InlineKeyboardButton("Option 3", callback_data="3")],
        [InlineKeyboardButton("Option 4", callback_data="4")],
        [InlineKeyboardButton("Option 5", callback_data="5")],
        [InlineKeyboardButton("Option 6", callback_data="6")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    state["WANT_PRICE"] = True

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")

# Define a function to handle messages
async def message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (state["WANT_PRICE"]):
        try:
            url = update.message.text
            domain = get_domain_name(url)
            css_selector = price_css_selectors[domain]
            price = await fetch_price(url, css_selector)
            await update.message.reply_text(f"The price is: {price}")
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
        state["WANT_PRICE"] = False
        #driver.execute_script("window.stop();")
        #driver.close()
    elif (state["HELP"]):
        text = update.message.text
        await update.message.reply_text(f"{text}")
        state["HELP"] = False

async def present_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        url, css_selector = update.message.text.split(" ", 1)
        price = await fetch_price(url, css_selector)
        await update.message.reply_text(f"The price is: {price}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
    #driver.execute_script("window.stop();")
    #driver.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I will echo text now.")
    state["HELP"] = True

def main() -> None:
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handle))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()

if __name__ == "__main__":
    main()
