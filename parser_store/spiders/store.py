import re
from datetime import datetime
from urllib.parse import urljoin

import scrapy

from parser_store.items import ParserStoreItem

current_date = datetime.now().timestamp()
BASE_URL = 'https://apteka-ot-sklada.ru'


def convert_price(price_text):
    return float(re.compile(r'[^\d.]').sub('', price_text))


class StoreSpider(scrapy.Spider):
    name = "store"
    allowed_domains = ["apteka-ot-sklada.ru"]
    start_urls = [
        ("https://apteka-ot-sklada.ru/catalog/sredstva-gigieny/"
         "uhod-za-polostyu-rta/zubnye-niti_-ershiki"),
        ("https://apteka-ot-sklada.ru/catalog/sredstva-gigieny/"
         "uhod-za-polostyu-rta/pasty-zubnye-detskie"),
        ("https://apteka-ot-sklada.ru/catalog/medikamenty-i-bady/"
         "vitaminy-i-mikroelementy/vitamin-e")
        ]

    # код города Томск
    cookies = {"city": "92"}

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                cookies=self.cookies,
                )

    def parse(self, response):
        goods_cat = response.css('div.goods-catalog-view__goods')
        goods_links = goods_cat.css('div.ui-card').css(
            'a::attr(href)').getall()
        for link in goods_links:
            yield response.follow(
                link,
                callback=self.parse_goods,
                cookies=self.cookies
                )

        next_page = response.xpath("//a[contains(., 'Далее')]/@href").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_goods(self, response):
        current_url = response.request.url

        goods_tags = response.css('li.goods-tags__item')
        marketing_tags = []
        for tag in goods_tags:
            text_tag = tag.css('span::text').get()
            marketing_tags.append(text_tag[5:-3])

        # Брэнд товара
        brand = response.xpath(
            '//div[@itemprop="manufacturer"]'
            ).xpath('//span[@itemtype="legalName"]/text()').get()

        # Иерархия разделов
        section = response.xpath(
            '//ul[@class="ui-breadcrumbs__list"]'
            ).xpath('//span[@itemprop="name"]/text()').getall()[2:-2]

        # Цена
        panel_price = response.xpath(
            '//div[@class="goods-offer-panel__price"]').css('span::text')
        price_data = {}
        if len(panel_price.getall()) == 1:
            price_data['current'] = convert_price(panel_price.getall()[0])
            price_data['original'] = price_data['current']
        elif len(panel_price.getall()) > 1:
            price_data['current'] = convert_price(panel_price.getall()[0])
            price_data['original'] = convert_price(panel_price.getall()[1])
            discount = 100 - (price_data['current']/price_data['original'])*100
            price_data['sale_tag'] = f"Скидка {discount:.2f}%"
        else:
            price_data = {}

        # Наличие товара
        stock = {}
        stock['in_stock'] = bool(
            response.xpath(
                '//ul[@class=("goods-offer-panel__records-list '
                'goods-offer-panel__part")]'
                ).css('span:contains("В наличии")').get())
        stock['count'] = 0

        # Ссылки на изображения товара
        goods_images = response.xpath(
            '//ul[@class="goods-gallery__preview-list"]'
            ).css('img::attr(src)')
        assets = {}
        assets['main_image'] = urljoin(BASE_URL, goods_images.get())
        set_images = []
        for image in goods_images:
            set_images.append(urljoin(BASE_URL, image.get()))
        assets['set_images'] = set_images
        assets['view360'] = []
        assets['video'] = []

        # Метаданные
        metadata = {}
        other_info = response.xpath(
            '//div[@class="goods-details-page__other-info"]')
        if other_info.css('h2:contains("Описание")').get():
            metadata['__description'] = ' '.join(
                other_info.css('p::text').re(r'\w.+'))
        metadata['СТРАНА ПРОИЗВОДИТЕЛЬ'] = response.xpath(
            '//div[@itemprop="manufacturer"]'
            ).xpath('//span[@itemtype="location"]/text()').get()

        data = {
                "timestamp": current_date,
                "RPC": re.findall(r'\d+$', current_url)[-1],
                "url": current_url,
                "title": response.css('h1').css('span::text').get(),
                "marketing_tags": marketing_tags,
                "brand": brand,
                "section": section,
                "price_data": price_data,
                "stock": stock,
                "assets": assets,
                "metadata": metadata,
            }
        yield ParserStoreItem(data)
