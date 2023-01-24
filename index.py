import scrapy
from dateutil import parser
from scrapy.crawler import CrawlerProcess
import sys


# python index.py <start_date> <end_date> <course>
# i.e. python index.py '19 April 2022' '19 April 2022' Epsom
# i.e. python index.py '15 April 2022' '21 April 2022' Cork

class PlacePotSpider(scrapy.Spider):
    name = 'placepot'
    custom_settings = {
        "FEED_URI": "output.csv",
        "FEED_FORMAT": "csv",
    }
    start_urls = ['https://rckongen.dk/collections/all']

    def start_requests(self):
        yield scrapy.Request('https://rckongen.dk/collections/all')

    def __init__(self):
        pass

    def getDate(self, string):
        dateString = string.split(":")[0][3:]
        try:
            return parser.parse(dateString)
        except:
            return False

    def cut(self, string, head):
        _, ans = string.split(head)
        return ans.strip()

    def getInfo(self, response):
        nameSelector = ".product-meta h1::text"
        skuSelector = ".product-meta__sku-number::text"
        priceSelector = ".price-list span"

        name = response.css(nameSelector).get()
        sku = "SKU"+ response.css(skuSelector).get()
        price = response.css(priceSelector).get().split("</span>")[1]
        yield {
            "Product Name": name,
            "SKU": sku,
            "Price": price,
            "Website name": "https://rckongen.dk/"
        }
    def crawlData(self, response):
        races = response.css("table tr h2::text").getall()
        # print("race: ", races)
        times = response.css("table tr h2 span.join::text").getall()
        # print("time: ", times)
        cols = response.css("table tr td div.row-fluid div.span2 p span::text").getall()
        # print("col: ", cols)
        rows = response.css(".span5 table.table.table-bordered tbody tr td::text").getall()
        # print("row: ", rows)

        raceDateString = response.css(".row-fluid .span10 h1::text").getall()[0]
        raceDateArray = raceDateString.split(" ")[-3:]
        raceDate = " ".join(raceDateArray)
        # print("date----------->", raceDate)


        alertString = response.css(".span10 .alert-block p span::text").getall()[0]
        alertArray = alertString.split(" ")

        dividEnd = alertArray[2][1: ]
        unit = alertArray[-2]
        # print(dividEnd, unit)
        p = 0
        for i in range(0, len(races)):
            race = races[i][:-3]
            time, course = times[i].split(' ')
            distance = self.cut(cols[3*i], 'Distance:')
            runners = self.cut(cols[3*i+1], 'Runners:')
            favourite = self.cut(cols[3*i+2], 'Favourite:')
            visit = False
            while p < len(rows):
                placed = rows[p]
                card_no = rows[p + 1]
                name = rows[p + 2]
                if(visit and placed == '1st'): break
                visit = True
                p += 3
                yield {
                    "date": raceDate,
                    "dividEnd": dividEnd,
                    "unit": unit,
                    "race": race,
                    "time": time,
                    "course": course,
                    "distance": distance,
                    "runners": runners,
                    "favourite": favourite,
                    "placed": placed,
                    "card_no": card_no,
                    "name": name
                }

    def parse(self, response):
        try:
            productSelector = ".product-list .product-item"
            items = response.css(productSelector)
            for item in items:
                link = item.css('a').attrib['href']
                yield scrapy.Request(f"https://rckongen.dk/{link}", callback=self.getInfo, dont_filter=True)

        except Exception as e:
            print("=====>error", e)

        # for items in response.css('.span10 p'):
        #     try: 
        #         date = self.getDate(items.getall()[0])
        #         if date == False:
        #             continue

        #         if date >= self.startDate and date <= self.endDate:

        #             courses = items.css('a')
        #             for course in courses:
        #                 text = course.css('::text').get()
        #                 if text == self.course:
        #                     link = course.attrib['href']
        #                     yield scrapy.Request(f"https://www.scoop6.co.uk{link}", callback=self.crawlData, dont_filter=True)
        #                 pass    
        #         pass
        #     except:
        #         yield {"error": "some error"}
        pass

process = CrawlerProcess()
process.crawl(PlacePotSpider)
process.start()

