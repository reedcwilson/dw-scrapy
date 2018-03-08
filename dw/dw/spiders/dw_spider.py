# -*- coding: utf-8 -*-
import scrapy


base_url = 'http://dw'


class DwSpiderSpider(scrapy.Spider):
    name = 'dw'
    allowed_domains = ['dw']
    start_urls = ['{}/Projects'.format(base_url)]

    def write_url(self, name, url):
        with open('urls.csv', 'a') as f:
            f.write('{},{}\n'.format(name, url))

    def clean_body(self, response, body):
        return body.replace('<h3 id="siteSub">From $1</h3>', '') \
                   .replace(response.css('#attachments').extract_first(), '') \
                   .replace(response.css('#comments').extract_first(), '')

    def parse(self, response):
        page = '|'.join(response.url.split("/")[3:])
        if (
                page.startswith('User:')
                or page.startswith('index.php')
                or page.startswith('Special:Tags')
           ):
                return
        self.write_url(page, response.url)
        filename = 'pages/{}.html'.format(page)
        try:
            with open(filename, 'w') as f:
                f.write(response.css('.t-title').extract_first())
                f.write(self.clean_body(response, response.css('.t-body').extract_first()))
            self.log('Saved file {}'.format(filename))
            for link in response.css('a::attr(href)'):
                link = link.extract()
                if (
                        link.startswith(base_url)
                        and 'deki' not in link
                   ):
                        yield scrapy.Request(response.urljoin(link), callback=self.parse)
        except Exception as e:
            with open('failed-pages.txt', 'a') as f:
                f.write(page)
