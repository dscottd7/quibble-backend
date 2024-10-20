import scrapy

class ExampleSpider(scrapy.Spider):
    name = "example"

    def __init__(self, url=None, *args, **kwargs):
        super(ExampleSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.scraped_data = []

    def parse(self, response):
        # Extract the entire HTML content of the page
        page_content = response.text
        self.scraped_data.append({'content': page_content})