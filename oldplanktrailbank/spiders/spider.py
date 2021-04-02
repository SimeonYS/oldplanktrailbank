import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import OoldplanktrailbankItem
from itemloaders.processors import TakeFirst
import json
pattern = r'(\xa0)?'
base = 'https://www.oldplanktrailbank.com/content/wintrust/oldplanktrailbank/en/small-business/resources/financial-education.article.{}.json?limit=10'

class OoldplanktrailbankSpider(scrapy.Spider):
	name = 'oldplanktrailbank'
	page = 0
	start_urls = [base.format(page)]

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['articles'])):
			link = data['articles'][index]['path']
			title = data['articles'][index]['title']
			date = data['articles'][index]['publishedDateLong']
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date, title=title))

		if not len(data['articles']) == 0:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response, date, title):

		content = response.xpath('//div[@class="article-main"]//text()[not (ancestor::div[@class="socialsharing-wrapper"] or ancestor::div[@class="articletags section"] or ancestor::div[@class="article-right-rail"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=OoldplanktrailbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
