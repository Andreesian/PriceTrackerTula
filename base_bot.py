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
    "dns-shop.ru": ".product-buy__price",
    "wildberries.ru": ".price-block__final-price", #https://www.wildberries.ru/catalog/18139480/detail.aspx
    "ozon.ru": ".np9", #https://www.ozon.ru/product/robot-pylesos-polaris-pvcr-1226-wi-fi-iq-home-gyro-chernyy-672452962/?avtc=1&avte=1&avts=1682763165&sh=rDKQSv7rkg
    "ozon.ru": ".n4p", #https://www.ozon.ru/product/robot-pylesos-polaris-pvcr-1226-wi-fi-iq-home-gyro-chernyy-672452962/?avtc=1&avte=1&avts=1682763165&sh=rDKQSv7rkg ww
    "lamoda.ru": "._price_t2bk4_7", #https://www.lamoda.ru/p/mp002xm08jab/clothes-colins-bryuki/
    "cdek.shopping": ".final-your-price__count", #https://cdek.shopping/p/60245/kroscovki-nike-air-force-1-shadow-belyi
    "leroymerlin.ru": "price.slot-container", #https://leroymerlin.ru/product/stul-premer-82x45x55-sm-derevo-cvet-belyy-84758318/
    "leroymerlin.ru": "._3ZkVWJ-JEE_pdp._2YOcEnUxeU_pdp", #https://leroymerlin.ru/product/ventilyator-napolnyy-monlan-mf-50sb-50-vt-52-sm-cvet-chernyy-84266575/
    "robo.market": ".styles__productPrice__6691", #https://robo.market/product/2982337
    "berito.ru": ".product__price", #https://www.berito.ru/product-plate-dlya-devochki-bombino-kiki-kids-430457/
    "kazanexpress.ru": ".currency", #https://kazanexpress.ru/product/Plate-TVOE-1554788
    "citilink.ru": ".app-catalog-1f8xctp", #https://www.citilink.ru/product/videokarta-msi-nvidia-geforce-rtx-3060-rtx-3060-ventus-2x-12g-oc-12gb-1475891/
    "pleer.ru": "price", #https://www.pleer.ru/_883840
    "onlinetrade.ru": ".js__actualPrice" #https://www.onlinetrade.ru/catalogue/kofemashiny-c1127/delonghi/kofemashina_delonghi_perfecta_evo_esam_420.40.b_0132217046-2415126.html
}

#state
state = {
    "START" : False,
    "HELP" : False,
    "WANT_PRICE" : False
}

async def fetch_price(url: str, css_selector: str) -> str:
    driver.get(url)
    element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    price = element.text.strip()
    return price

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Категория 1", callback_data="1")],
        [InlineKeyboardButton("Категория 2", callback_data="2")],
        [InlineKeyboardButton("Категория 3", callback_data="3")],
        [InlineKeyboardButton("Категория 4", callback_data="4")],
        [InlineKeyboardButton("Категория 5", callback_data="5")],
        [InlineKeyboardButton("Категория 6", callback_data="6")],
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
