import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

import configparser

import re

import secrets

def generate_unique_id(num_bits=63):
    return secrets.randbits(num_bits)

def trim_currency(text):
    pattern = r'[^\d]'
    trimmed_text = re.sub(pattern, '', text)
    decimal_index = trimmed_text.find('.')
    if decimal_index != -1:
        trimmed_text = trimmed_text[:decimal_index]

    return trimmed_text

def load_api_key(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    if "api" in config.sections() and "key" in config["api"]:
        return config["api"]["key"]
    else:
        raise KeyError("API key not found in the configuration file")
    
def load_db_cfg(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    if "database" in config.sections() and "name" in config["database"] and "user" in config["database"] and "password" in config["database"] and "host" in config["database"] and "port" in config["database"]:
        return [config["database"]["name"], config["database"]["user"], config["database"]["password"], config["database"]["host"], config["database"]["port"]]
    else:
        raise KeyError("Database config not found in the configuration file")

def get_current_date():
    current_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

async def daily_task():
    while True:
        get_current_date()
        current_time = datetime.utcnow()
        next_run_time = (current_time + timedelta(seconds=5)).replace(hour=0, minute=0, second=0, microsecond=0)
        sleep_duration = 3600
        await asyncio.sleep(sleep_duration)

from database import (
    get_user_state_by_id,
    get_user_by_nickname,
    get_request_by_product_name,
    get_url_by_url,
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
    "pleer.ru": ".product_info" #https://www.pleer.ru/search_iphone+13.html
}

image_css_selectors = {
    "dns-shop.ru": ".product-images-slider__main-img", #https://www.dns-shop.ru/search/?q=rtx+3070&category=17a89aab16404e77
    "wildberries.ru": ".slide__content.img-plug.j-wba-card-item", #https://www.wildberries.ru/catalog/25742723/detail.aspx
    "ozon.ru": ".k7z.z7-a", #https://www.ozon.ru/product/robot-pylesos-polaris-pvcr-1226-wi-fi-iq-home-gyro-chernyy-672452962/?avtc=1&avte=1&avts=1682802352&sh=rDKQSuvh-w
    "lamoda.ru": "._root_1wiwn_3._image_i5mcd_2._image_i5mcd_2", #https://www.lamoda.ru/p/rtlack938201/clothes-ea7-kostyum-sportivnyy/
    "cdek.shopping": ".item", #https://cdek.shopping/p/60245/kroscovki-nike-air-force-1-shadow-belyi
    "leroymerlin.ru": "#picturesWrapper", #https://leroymerlin.ru/product/ventilyator-napolnyy-monlan-mf-50sb-50-vt-52-sm-cvet-chernyy-84266575/
    "robo.market": ".Image-module__centered__0dda.styles__activeImage__0e5d.styles__imageStyle__7186", #https://robo.market/product/1807193
    "berito.ru": ".product__gallery-image", #https://www.berito.ru/product-plate-v-goroshek-noname-4411163/
    "kazanexpress.ru": ".product-page-container.product-info-card.photos-container.main-photo.carousel-container.img", #delete .img if doesnt works anyw https://kazanexpress.ru/product/Belaya-krem---1742409
    "citilink.ru": ".ekkbt9g0.app-catalog-15kpwh2.e1fcwjnh0", #https://www.citilink.ru/product/videokarta-msi-nvidia-geforce-rtx-3060-rtx-3060-ventus-2x-12g-oc-12gb-1475891/
    "pleer.ru": ".photo_self_section.a.img" #https://www.pleer.ru/_955714
}

product_name_css_selectors = {
    "dns-shop.ru": ".product-card-top__title", #https://www.dns-shop.ru/product/bb884500ae092ff1/videokarta-palit-geforce-rtx-3070-ti-gamingpro-ned307t019p2-1046a/
    "wildberries.ru": ".product-page__header h1", #https://www.wildberries.ru/catalog/25742723/detail.aspx
    "ozon.ru": ".n2q", #https://www.ozon.ru/product/robot-pylesos-polaris-pvcr-1226-wi-fi-iq-home-gyro-chernyy-672452962/?avtc=1&avte=1&avts=1682802352&sh=rDKQSuvh-w
    "lamoda.ru": "._modelName_rumwo_22", #https://www.lamoda.ru/p/rtlack938201/clothes-ea7-kostyum-sportivnyy/
    "cdek.shopping": ".product-header-name h1", #https://cdek.shopping/p/60245/kroscovki-nike-air-force-1-shadow-belyi
    "leroymerlin.ru": ".t12nw7s2_pdp", #https://leroymerlin.ru/product/ventilyator-napolnyy-monlan-mf-50sb-50-vt-52-sm-cvet-chernyy-84266575/
    "robo.market": ".styles__productArticleTitle__8e33", #https://robo.market/product/1807193
    "berito.ru": ".page-header__title", #https://www.berito.ru/product-plate-v-goroshek-noname-4411163/
    "kazanexpress.ru": ".info-block.base h1", #https://kazanexpress.ru/product/Belaya-krem---1742409
    "citilink.ru": ".e1ubbx7u0.eml1k9j0.app-catalog-tn2wxd.e1gjr6xo0", #https://www.citilink.ru/product/videokarta-msi-nvidia-geforce-rtx-3060-rtx-3060-ventus-2x-12g-oc-12gb-1475891/
    "pleer.ru": ".product_info a.href" #https://www.pleer.ru/_653047
}

query_css_selectors = {
    "dns-shop.ru": "/search/?q=", #https://www.dns-shop.ru/search/?q=rtx+3070&category=17a89aab16404e77
    "wildberries.ru": "/catalog/0/search.aspx?search=", #https://www.wildberries.ru/catalog/0/search.aspx?search=масло
    "ozon.ru": "/search/?text=", #https://www.ozon.ru/search/?text=масло&from_global=true
    "lamoda.ru": "/catalogsearch/result/?q=", #https://www.lamoda.ru/catalogsearch/result/?q=tommy&submit=y&gender_section=men
    "cdek.shopping": "/?digiSearch=true&term=", #https://cdek.shopping/p/60245/kroscovki-nike-air-force-1-shadow-belyi
    "leroymerlin.ru": "/search/?q=", #https://leroymerlin.ru/search/?q=обои&suggest=true
    "robo.market": "/catalog?text=", #https://robo.market/catalog?text=Белый&page_number=1
    "berito.ru": "/search/?query=", #https://www.berito.ru/search/?query=Белый
    "kazanexpress.ru": "/search?query=", #https://kazanexpress.ru/search?query=белый&needsCorrection=0
    "citilink.ru": "/search/?text=", #https://www.citilink.ru/search/?text=белый
    "pleer.ru": "/search_" #https://www.pleer.ru/search_белый.html
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
    "pleer.ru": ".price" #https://www.pleer.ru/_883840
}

state = {
    "START" : False,
    "ECHO" : False,
    "WANT_PRICE_LINK" : False,
    "WANT_PRICE_QUERY" : False
}

state_dict = {
    0 : "START",
    1 : "TEST"
}

swap_value = {}

def id_generator():
    id_value = 0
    while True:
        yield id_value
        id_value += 1

unique_id = id_generator()

async def fetch_item_name(url: str, css_selector: str) -> str:
    driver.get(url)
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    name = element.text.strip()
    return name

async def fetch_first_item_url(url: str, css_selector: str) -> str:
    driver.get(url)
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    href = element.get_attribute("href")
    return href

async def fetch_price(url: str, css_selector: str) -> str:
    driver.get(url)
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    price = element.text.strip()
    return price

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global connection
    user = update.effective_user
    username = user.full_name
    if get_user_by_nickname(connection, user.full_name) == None:
        add_user(connection, generate_unique_id(), username)
    keyboard = [
        [InlineKeyboardButton("📦Общее", callback_data="general")],
        [InlineKeyboardButton("👖Одежда и обувь", callback_data="cloth")],
        [InlineKeyboardButton("💄Косметика", callback_data="cosmetics")],
        [InlineKeyboardButton("🛋️Мебель, декор", callback_data="decor")],
        [InlineKeyboardButton("🔌Оборудование и техника", callback_data="tech")],
        [InlineKeyboardButton("🧺Продукты", callback_data="groceries")],
        [InlineKeyboardButton("🧸Детское", callback_data="child")],
        [InlineKeyboardButton("🌐Ссылка", callback_data="link")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите категорию либо ввод по ссылке:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global connection
    query = update.callback_query
    await query.answer()
    #await query.edit_message_text(text=f"Selected option: {query.data}")
    if (query.data == "link"):
        await query.edit_message_text(text=f"🗒Введите ссылку на товар:")
        state["WANT_PRICE_LINK"] = True
    if (query.data == "add_to_list"):
        request_id_toadd = generate_unique_id()
        new_reqs = get_user_by_nickname(connection, update.effective_user.full_name)[2]
        new_reqs.append(request_id_toadd)
        add_request(connection, request_id_toadd, swap_value[update.effective_user.full_name][0], "1 day", [int(trim_currency(swap_value[update.effective_user.full_name][2]))], get_url_by_url(connection, swap_value[update.effective_user.full_name][1])[0])
        update_user(connection, get_user_by_nickname(connection, update.effective_user.full_name)[0], new_request_ids=new_reqs)
        await query.edit_message_text(text=f"✅Товар добавлен в ваш список уведомлений!")
    if (query.data == "dont_add_to_list"):
        await query.edit_message_text(text=f"❌Товар не был добавлен в ваш список уведомлений")
    if (query.data == 'tech'):
        state["WANT_PRICE_QUERY"] = True
        await query.edit_message_text(text=f"🗒Введите название товара:")
    if (query.data == 'daily'):
        await query.edit_message_text(text=f"✅Частота обновления установлена на: ежедневно")
    if (query.data == 'weekly'):
        await query.edit_message_text(text=f"✅Частота обновления установлена на: еженедельно")

async def message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global swap_value
    if (state["WANT_PRICE_LINK"]):
        try:
            url = update.message.text
            domain = get_domain_name(url)
            price_css_selector = price_css_selectors[domain]
            name_css_selector = product_name_css_selectors[domain]
            await update.message.reply_text(f"⚙Загружаем цены...")
            name = await fetch_item_name(url, name_css_selector)
            await update.message.reply_text(f"🏷Название товара: {name}")
            price = await fetch_price(url, price_css_selector)
            await update.message.reply_text(f"🏷Цена товара: {price}")
            keyboard = [
                [InlineKeyboardButton(f'✅Да', callback_data="add_to_list")],
                [InlineKeyboardButton(f'❌Нет', callback_data="dont_add_to_list")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if (get_url_by_url(connection, url)) == None:
                add_url(connection, generate_unique_id(), url, name)
            await update.message.reply_text("🔔Желаете ли вы добавить этот товар в список ваших уведомлений?", reply_markup=reply_markup)
            swap_value[update.effective_user.full_name] = []
            swap_value[update.effective_user.full_name].append(name)
            swap_value[update.effective_user.full_name].append(url)
            swap_value[update.effective_user.full_name].append(price)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
        state["WANT_PRICE"] = False
        #driver.execute_script("window.stop();")
        #driver.close()
    elif (state["ECHO"]):
        text = update.message.text
        await update.message.reply_text(f"{text}")
        state["ECHO"] = False
    elif (state["WANT_PRICE_QUERY"]):
        text = update.message.text
        await update.message.reply_text(f"⚙Загружаем товары с площадок... (Это может занять некоторое время...)")
        await update.message.reply_text(f"❗Пока идет поиск, предлагаем вам предложение от наших партнеров!")
        item_url = []
        url = "https://dns-shop.ru/search/?q=" + text
        #await update.message.reply_text(f"{search_css_selectors['dns-shop.ru']}")
        item_url.append(await fetch_first_item_url(url, search_css_selectors['dns-shop.ru']))
        #await update.message.reply_text(f"{item_url}")
        url = "https://www.citilink.ru/search/?text=" + text
        #await update.message.reply_text(f"{search_css_selectors['citilink.ru']}")
        item_url.append(await fetch_first_item_url(url, search_css_selectors['citilink.ru']))
        #await update.message.reply_text(f"{item_url}")
        url = "https://www.wildberries.ru/catalog/0/search.aspx?search=" + text
        #await update.message.reply_text(f"{search_css_selectors['citilink.ru']}")
        item_url.append(await fetch_first_item_url(url, search_css_selectors['wildberries.ru']))
        #await update.message.reply_text(f"{item_url}")
        await update.message.reply_text(f"⚙Загружаем цены с площадок...")
        prices = []
        prices.append(await fetch_price(item_url[0], price_css_selectors['dns-shop.ru']))
        prices.append(await fetch_price(item_url[1], price_css_selectors['citilink.ru']))
        prices.append(await fetch_price(item_url[2], price_css_selectors['wildberries.ru']))
        final = ""
        final += "🏷Цена в DNS: " + prices[0] + "\n"
        final += "🏷Цена в Citilink: " + prices[1] + "₽\n"
        final += "🏷Цена в Wildberries: " + prices[2] + "\n"
        await update.message.reply_text(f"{final}")
        keyboard = [
            [InlineKeyboardButton(f'✅Да', callback_data="add_to_list")],
            [InlineKeyboardButton(f'❌Нет', callback_data="dont_add_to_list")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🔔Желаете ли вы добавить этот товар в список ваших уведомлений?", reply_markup=reply_markup)
        state["WANT_PRICE_QUERY"] = False

async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I will echo text now.")
    state["ECHO"] = True

async def start_waiting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await daily_task()

async def list_notifs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = get_user_by_nickname(connection, update.effective_user.full_name)[0]
    request_ids = get_user_by_nickname(connection, update.effective_user.full_name)[2]
    for request in request_ids:
        await update.message.reply_text(get_request_by_id(connection, request)[1])

async def view_price_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    request_ids = get_user_by_nickname(connection, update.effective_user.full_name)[2]
    for request in request_ids:
        await update.message.reply_text(get_request_by_id(connection, request)[1])

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
            [InlineKeyboardButton(f'🕑Ежедневно (💸Только премиум подписка)', callback_data="daily")],
            [InlineKeyboardButton(f'🕑Еженедельно', callback_data="weekly")],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("❓Как часто следует проверять ваши товары на изменение цены?", reply_markup=reply_markup)

def main() -> None:
    global connection
    config_file = "config.cfg"
    api_key = load_api_key(config_file)
    database_cfg = load_db_cfg(config_file)
    connection = create_connection(database_cfg[0], database_cfg[1], database_cfg[2], database_cfg[3], database_cfg[4])
    application = Application.builder().token(api_key).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handle))
    application.add_handler(CommandHandler("echo", echo_command))
    application.add_handler(CommandHandler("wait", start_waiting, block=False))
    application.add_handler(CommandHandler("list", list_notifs))
    application.add_handler(CommandHandler("settings", settings))

    application.run_polling()
    
if __name__ == "__main__":
    
    main()