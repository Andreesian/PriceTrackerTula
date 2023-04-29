import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

import configparser

def load_api_key(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    if "api" in config.sections() and "key" in config["api"]:
        return config["api"]["key"]
    else:
        raise KeyError("API key not found in the configuration file")

def get_current_date():
    current_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Current date: {current_date}")

async def daily_task():
    while True:
        get_current_date()
        current_time = datetime.utcnow()
        next_run_time = (current_time + timedelta(seconds=5)).replace(hour=0, minute=0, second=0, microsecond=0)
        sleep_duration = 5

        print(f"Sleeping for {sleep_duration} seconds")
        await asyncio.sleep(sleep_duration)
        print(f"sleeped")

from database import (
    create_connection,
    close_connection,
    add_user,
    add_request,
    add_url,
    get_user_by_id,
    get_request_by_id,
    get_url_by_id,
    update_user,
    update_request,
    update_url,
    delete_user,
    delete_request,
    delete_url
)

connection = create_connection("sell_bot", "postgres", "333221", "localhost", "5432")

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
    "dns-shop.ru": ".catalog-product__name.ui-link.ui-link_black", #https://www.dns-shop.ru/search/?q=rtx+3070&category=17a89aab16404e77
    "wildberries.ru": ".product-card__link.j-card-link.j-open-full-product-card", #https://www.wildberries.ru/catalog/0/search.aspx?search=rtx%203070
    "ozon.ru": ".tile-hover-target.yj4.jy5", #https://www.ozon.ru/category/videokarty-15721/?category_was_predicted=true&deny_category_prediction=true&from_global=true&text=rtx+3070
    "lamoda.ru": "._root_clp6c_2._label_clp6c_17.x-product-card__pic.x-product-card__pic-catalog.x-product-card__pic.x-product-card__pic-catalog", #https://www.lamoda.ru/catalogsearch/result/?q=tommy&submit=y&gender_section=men
    "cdek.shopping": ".digi-product__image-wrapper", #https://cdek.shopping/?digiSearch=true&term=force&params=%7Csort%3DDEFAULT
    "leroymerlin.ru": ".bex6mjh_plp.b1f5t594_plp.iypgduq_plp.nf842wf_plp", #https://leroymerlin.ru/search/?q=обои&suggest=true
    "robo.market": ".Product-module__imageWrapper__a729", #https://robo.market/catalog?text=iphone%2013&page_number=1
    "berito.ru": ".snippet__photo-wrapper", #https://www.berito.ru/search/?query=платье
    "kazanexpress.ru": ".subtitle-item", #https://kazanexpress.ru/search?query=iphone%2014%20pro%20max&needsCorrection=0
    "citilink.ru": ".app-catalog-9gnskf.e1259i3g0", #https://www.citilink.ru/product/videokarta-msi-nvidia-geforce-rtx-3060-rtx-3060-ventus-2x-12g-oc-12gb-1475891/
    "pleer.ru": ".product_preview_img" #https://www.pleer.ru/search_iphone+13.html
}


price_css_selectors = {
    "dns-shop.ru": ".product-buy__price",
    "wildberries.ru": ".price-block__final-price", #https://www.wildberries.ru/catalog/18139480/detail.aspx
    "ozon.ru": ".np9", #https://www.ozon.ru/product/robot-pylesos-polaris-pvcr-1226-wi-fi-iq-home-gyro-chernyy-672452962/?avtc=1&avte=1&avts=1682763165&sh=rDKQSv7rkg
    "ozon.ru": ".n4p", #https://www.ozon.ru/product/robot-pylesos-polaris-pvcr-1226-wi-fi-iq-home-gyro-chernyy-672452962/?avtc=1&avte=1&avts=1682763165&sh=rDKQSv7rkg ww
    "lamoda.ru": "._price_t2bk4_7", #https://www.lamoda.ru/p/mp002xm08jab/clothes-colins-bryuki/
    "cdek.shopping": ".final-your-price__count", #https://cdek.shopping/p/60245/kroscovki-nike-air-force-1-shadow-belyi
    "leroymerlin.ru": ".price.slot-container", #https://leroymerlin.ru/product/stul-premer-82x45x55-sm-derevo-cvet-belyy-84758318/
    "leroymerlin.ru": "._3ZkVWJ-JEE_pdp._2YOcEnUxeU_pdp", #https://leroymerlin.ru/product/ventilyator-napolnyy-monlan-mf-50sb-50-vt-52-sm-cvet-chernyy-84266575/
    "robo.market": ".styles__productPrice__6691", #https://robo.market/product/2982337
    "berito.ru": ".product__price", #https://www.berito.ru/product-plate-dlya-devochki-bombino-kiki-kids-430457/
    "kazanexpress.ru": ".currency", #https://kazanexpress.ru/product/Plate-TVOE-1554788
    "citilink.ru": ".app-catalog-1f8xctp", #https://www.citilink.ru/product/videokarta-msi-nvidia-geforce-rtx-3060-rtx-3060-ventus-2x-12g-oc-12gb-1475891/
    "pleer.ru": "price" #https://www.pleer.ru/_883840
}

#state
state = {
    "START" : False,
    "HELP" : False,
    "WANT_PRICE" : False
}

def id_generator():
    id_value = 0
    while True:
        yield id_value
        id_value += 1

unique_id = id_generator()

async def fetch_price(url: str, css_selector: str) -> str:
    driver.get(url)
    element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    price = element.text.strip()
    return price

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global connection
    user = update.effective_user
    username = user.full_name
    add_user(connection, next(unique_id), username)
    keyboard = [
        [InlineKeyboardButton("📦Общее", callback_data="1")],
        [InlineKeyboardButton("👖Одежда и обувь", callback_data="2")],
        [InlineKeyboardButton("💄Косметика", callback_data="3")],
        [InlineKeyboardButton("🛋️Мебель, декор", callback_data="4")],
        [InlineKeyboardButton("🔌Оборудование и техника", callback_data="5")],
        [InlineKeyboardButton("🧺Продукты", callback_data="6")],
        [InlineKeyboardButton("🧸Детское", callback_data="6")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    global connection
    query = update.callback_query
    state["WANT_PRICE"] = True

    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")
    if (query.data == "add_to_list"):
        add_request(connection, next(unique_id), "default", "1 day", [], 1)
        update_user(connection, next(unique_id), new_request_ids=[get_request_by_id(connection, 1)[0]])
        await query.edit_message_text(text=f"✅Товар добавлен в ваш список уведомлений!")

# Define a function to handle messages
async def message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (state["WANT_PRICE"]):
        try:
            url = update.message.text
            domain = get_domain_name(url)
            css_selector = price_css_selectors[domain]
            await update.message.reply_text(f"⚙Загружаем цены...")
            price = await fetch_price(url, css_selector)
            await update.message.reply_text(f"🏷Цена товара: {price}")
            keyboard = [
                [InlineKeyboardButton(f'✅Да', callback_data="add_to_list")],
                [InlineKeyboardButton(f'❌Нет', callback_data="dont_add_to_list")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🔔Желаете ли вы добавить этот товар в список ваших уведомлений?", reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
        state["WANT_PRICE"] = False
        #driver.execute_script("window.stop();")
        #driver.close()
    elif (state["HELP"]):
        text = update.message.text
        await update.message.reply_text(f"{text}")
        state["HELP"] = False

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I will echo text now.")
    state["HELP"] = True

async def start_waiting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await daily_task()

def main() -> None:
    global connection
    config_file = "config.cfg"
    api_key = load_api_key(config_file)
    application = Application.builder().token(api_key).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handle))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("wait", start_waiting, block=False))

    application.run_polling()
    

if __name__ == "__main__":
    main()