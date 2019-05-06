
from scrapy import Spider, Request
from zocdoc.items import ZocdocItem
import re
from collections import defaultdict


class ZocdocSpider(Spider):
    name = 'zocdoc_spider'
    allowed_urls = ['https://www.zocdoc.com/']
    start_urls = ['https://www.zocdoc.com/morespecialties']
    file = open('url_list.txt', 'w')

    def parse(self, response):
        spec1 = response.xpath('.//div[@class="column  first TwoColumn "]//a/@href').extract() 
        spec2 = response.xpath('.//div[@class="column TwoColumn "]//a/@href').extract() 
        allSpec = spec1 + spec2
        zipcodes = ["10018", "11366", "10308", "11212", "10453", "10026"]
        counter = defaultdict(int)
        for spec in allSpec:
            for zipcode in zipcodes:
                for page in range(1, 11):
                    url = "http://www.zocdoc.com" + spec + "/" + str(page) + "?address=" + zipcode
                #url = "http://www.zocdoc.com" + spec
                    # counter[zipcode] += 1
                    # print('='*50)
                    # print(counter)
                    # print('='*50)
                    yield Request(url = url, meta = {'zipcode': zipcode, 'page': page, "spec": spec}, callback = self.parse_doctors)


    def parse_doctors(self, response):
        docNamesUrl = response.xpath('.//div[@class="sc-171g4h3-0 fjWEnB"]//a/@href').extract()
        # print(len(docNamesUrl))
        zipcode = response.meta.get("zipcode", None)
        page = response.meta.get("page", None)
        for url in docNamesUrl:
            self.file.write(url + '\n')
        for name in docNamesUrl:
            nameUrl = "http://www.zocdoc.com" + name
            yield Request(url = nameUrl, meta = {'zipcode': zipcode, 'page': page}, callback = self.parse_doctors_reviews)

    #def parse_review_kv(self, response):
        #for section in response.xpath('.//section[@class="krbmlv-0 EdZTS"]'):
            #header = section.xpath('./h2/span/text()').extract_first()

    def parse_doctors_reviews(self, response):
        #docNames = response.xpath('.//div[@class="sc-1s83c7v-1 dKpLdn ofapnq-0 iCNHsn"]//span/text()').extract()[1]
        docNames = response.xpath('.//div[@class="sc-1s83c7v-1 dKpLdn ofapnq-0 iCNHsn"]/h1/span/text()').extract_first()
        specialty = response.xpath('.//div[@class="sc-1s83c7v-1 dKpLdn ofapnq-0 iCNHsn"]//h2/text()').extract_first()
        rating = response.xpath('.//div[@class="sc-15uikgc-1 fIgSnr"]/text()').extract_first() 
        numReviews = response.xpath('.//div[@class="sc-15uikgc-3 dOTRWJ"]//span/button/span/text()').extract_first()
        gender = response.xpath('.//section[@class="krbmlv-0 EdZTS"]/p/text()').extract()[0]
        awards = response.xpath('.//div[@class="sc-19iyn37-3 ijlwZZ"]/span/text()').extract()

        language = ""
        for i in range(len(response.xpath('.//section[@class="krbmlv-0 EdZTS"]'))):
            if response.xpath('.//section[@class="krbmlv-0 EdZTS"]')[i].xpath('.//text()').extract()[0] == "Languages spoken": 
                    language = response.xpath('.//section[@class="krbmlv-0 EdZTS"]')[i].xpath('.//text()').extract()[1:] 

        #language = response.xpath('.//li[@class="krbmlv-3 hsNEfT"]/text()').extract()
        zipCode = response.xpath('.//div[@class="sc-1h2t0vx-2 kGLUtF"]/p/span/text()').extract()[2]
        pageNum = response.meta.get("page", None)
        try:
            latitude = response.xpath('.//div[@class="sc-1h2t0vx-0 kGozZf"]//meta/@content').extract()[0]
            longitude = response.xpath('.//div[@class="sc-1h2t0vx-0 kGozZf"]//meta/@content').extract()[1]
        except:
            latitude = ""
            longitude = ""


        item = ZocdocItem()
        item['docNames'] = docNames
        item['specialty'] = specialty
        item['rating'] = rating
        item['numReviews'] = numReviews
        item['language'] = language
        item['gender'] = gender
        item['awards'] = awards
        item['zipCode'] = zipCode
        item['pageNum'] = pageNum
        item['latitude'] = latitude
        item['longitude'] = longitude
        yield item


