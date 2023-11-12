from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# https://www.smogon.com/dex/
# https://www.smogon.com/dex/sv/pokemon/
# https://www.smogon.com/dex/sv/pokemon/abomasnow/

chrome_driver_path = "smogon_web_scraper\\vendor\\chrome-driver\\chromedriver.exe"


class SmogonCrawlerSpider(CrawlSpider):
    name = "smogon-crawler"
    allowed_domains = ["www.smogon.com"]
    start_urls = ["https://www.smogon.com/dex/"]

    rules = (
        Rule(LinkExtractor(allow="dex", deny="pokemon")),
        Rule(LinkExtractor(allow="pokemon"), callback="parse_item"),
    )

    def __init__(self, *a, **kw):
        super(SmogonCrawlerSpider, self).__init__(*a, **kw)
        self.driver = webdriver.Chrome()

    def parse_start_url(self, response):
        return self.parse_item(response)

    def parse_item(self, response):
        self.driver.get(response.url)
        if response.url != "https://www.smogon.com/dex/":
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "PokemonAltRow-name"))
            )
        body = self.driver.page_source
        sel = Selector(text=body)
        return {
            "url": response.url,
            "title": sel.css("title::text").get(),
            "links": sel.css("div.PokemonAltRow-name > a::attr(href)").getall(),
        }

    def closed(self, reason):
        # Close the Selenium WebDriver when the spider is closed
        self.driver.quit()
