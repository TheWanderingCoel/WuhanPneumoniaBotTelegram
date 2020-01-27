import re
import requests
import warnings
import json
import time
import telegram
from flask import Flask, request
from telegram.ext import Dispatcher, CommandHandler
from Config import config

warnings.filterwarnings('ignore')


class nCov:

    def __init__(self):
        # Uncomment below two lines if you are in China
        # proxy = telegram.utils.request.Request(proxy_url='socks5://127.0.0.1:1086')
        # self.bot = telegram.Bot(token=config["Telegram"]["TOKEN"], request=proxy)
        # And comment the line below
        self.bot = telegram.Bot(token=config["Telegram"]["TOKEN"])
        self.bot.set_webhook(config["Telegram"]["WEBHOOK"])
        self.text = "🇨🇳武汉肺炎疫情查询\n" \
                    "Powered by 2020 TheWanderingCoel with love❤️\n" \
                    "🎈灵感来源于方糖\n\n"

    def work(self):
        app = Flask(__name__)

        @app.route('/', methods=['POST'])
        def webhook_handler():
            """Set route / with POST method will trigger this method."""
            if request.method == "POST":
                update = telegram.Update.de_json(request.get_json(force=True), self.bot)

                # Update dispatcher process that handler to process this message
                self.dispatcher.process_update(update)
            return 'ok'

        self.dispatcher = Dispatcher(self.bot, None)
        self.dispatcher.add_handler(CommandHandler('overview', self.message_handler))
        self.dispatcher.add_handler(CommandHandler('status', self.message_handler))
        self.dispatcher.add_handler(CommandHandler('news', self.message_handler))
        self.dispatcher.add_handler(CommandHandler('rumors', self.message_handler))
        app.run(host=config["Flask"]["HOST"], port=config["Flask"]["PORT"], debug=True)

    def get_data(self, category):
        url = "https://3g.dxy.cn/newh5/view/pneumonia"
        resp = requests.get(url).content.decode("utf-8")
        if category == "overview":
            reg = r'<script id="getStatisticsService">.+?window.getStatisticsService\s=\s(.+?)\}catch\(e\)\{\}</script>'
        elif category == "news":
            reg = r'<script id="getTimelineService">.+?window.getTimelineService\s=\s(\[.+?\])\}catch\(e\)\{\}</script>'
        elif category == "distribution":
            reg = r'<script id="getAreaStat">.+?window.getAreaStat\s=\s(\[.+?\])\}catch\(e\)\{\}</script>'
        elif category == "rumors":
            reg = r'<script id="getIndexRumorList">.+?window.getIndexRumorList\s=\s(\[.+?\])\}catch\(e\)\{\}</script>'
        result = re.search(reg, resp).group(1)
        data = json.loads(result)
        return data

    def reply_status(self, name):
        data = self.get_data("status")
        # If name is Provience
        for each in data:
            if name in each["provinceName"]:
                return self.make_text(each)
        # If name is City
        for each in data:
            for city in each["cities"]:
                if name in city["cityName"]:
                    name = each["provinceShortName"]
                    return self.make_text(each)

    def reply_overview(self):
        data = self.get_data("overview")
        text = self.text + data["countRemark"]
        cmap = data["imgUrl"]
        stat = data["dailyPic"]
        return text, cmap, stat

    def make_text(self, data):
        text = self.text
        for city in data["cities"]:
            confirmCount = city["confirmedCount"]
            text += city["cityName"] + f" 确认{confirmCount}例" + "\n"
        text += " ⏱ " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n"
        text += "💊 全国疫情 → t.cn/A6v1xgC0"
        return text

    def message_handler(self, bot, update):
        text = update.message.text
        if "/overview" in text:
            response, cmap, stat = self.reply_overview()
            update.message.reply_text(response)
            update.message.reply_photo(photo=cmap)
            update.message.reply_photo(photo=stat)
        elif "/news" in text:
            data = self.get_data("news")
            update.message.reply_text(self.text)
            for each in data:
                text = "*" + each["title"] + "*" + "\n\n" + each["summary"]
                update.message.reply_text(text, parse_mode='Markdown', quote=False)
        elif "/status" in text:
            response = self.reply_status(text.replace("/status ", ""))
            update.message.reply_text(response)
        elif "/rumors" in text:
            data = self.get_data("rumors")
            update.message.reply_text(self.text)
            for each in data:
                text = "*" + each["title"] + "*" + "\n\n" + each["summary"]
                update.message.reply_text(text, parse_mode='Markdown', quote=False)

nCov = nCov()
nCov.work()
