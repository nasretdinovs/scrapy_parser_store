BOT_NAME = "parser_store"

SPIDER_MODULES = ["parser_store.spiders"]
NEWSPIDER_MODULE = "parser_store.spiders"

ROBOTSTXT_OBEY = True

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
FEEDS = {
    'data/goods_%(time)s.json': {
        'format': 'json',
        'overwrite': True
    },
}
