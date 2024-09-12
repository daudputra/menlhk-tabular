from playwright.async_api import async_playwright
from scrapy import Selector

from src.helper.save_json import SaveJson
from src.helper.upload_s3 import upload_to_s3

import asyncio
import os

class MainController:

    def __init__(self, url, headless=False, miniwin=False, s3=False) -> None:
        self.url_page = url
        self.headless = headless
        self.miniwin = miniwin
        self.uploads3 = s3

    async def main(self):
        async with async_playwright() as pw:
            viewports = {'width': 500, 'height': 500} if self.miniwin and not self.headless else None
            

            try:
                #? launch chromium
                browser = await pw.chromium.launch(headless=self.headless)
                context = await browser.new_context(viewport=viewports) 
                page = await context.new_page()
                await page.goto(self.url_page, timeout=1800000)
                await asyncio.sleep(5)


                await self.close_banner(page)



                #? click category
                categories = page.locator('//*[@id="nav-tabular"]/li/a')
                count = await categories.count()

                for i in range(count):
                    category = categories.nth(i) 
                    category_text = await category.inner_text()
                    print(category_text)
                    await category.click()  
                    await asyncio.sleep(3) 

                    # await page.wait_for_selector('#tabular-card-7 > div.card-body > div > div > div.spinner', state='hidden', timeout=60000)
                    await page.wait_for_selector('.tab-pane > div:nth-child(1)', state='hidden', timeout=60000)

                    
                    # ? click sub category
                    sub_categories = page.locator('//html/body/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div[1]/div/div/ul/li')
                    count = await sub_categories.count()

                    for j in range(count):
                        sub_category = sub_categories.nth(j)
                        sub_category_text = await sub_category.inner_text()
                        print(sub_category_text)
                        await sub_category.click()
                        await asyncio.sleep(3)


                        # await page.wait_for_selector('#tabular-card-7 > div.card-body > div > div > div.spinner', state='hidden', timeout=300000)
                        await page.wait_for_selector('.tab-pane > div:nth-child(1)', state='hidden', timeout=300000)

                        tahun_options = page.locator('//html/body/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/div[1]/form/div/div[1]/div/div/select/option')
                        count = await tahun_options.count()


                        for t in range(count): 
                            tahun_option = tahun_options.nth(t)
                            tahun_value = await tahun_option.get_attribute('value')
                            await page.locator('//html/body/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/div[1]/form/div/div[1]/div/div/select').select_option(tahun_value)
                            tahun_text = await tahun_option.inner_text()
                            print(tahun_text)
                            await asyncio.sleep(3)

                            await page.wait_for_selector('text=FILTER', timeout=300000)
                            await page.locator('text=FILTER').click()

                            await asyncio.sleep(5)
                            data = await self._get_table_data(page)

                            filename = f"{category_text.lower().replace(' ','_')}_{sub_category_text.lower().replace(' ','_')}_{tahun_text}.json"
                            path_data_raw = f's3://ai-pipeline-raw-data/data/data_statistics/satu_data_kementrian_lingkungan_hidup_dan_kehutanan/{category_text.lower().replace(' ','_')}/{sub_category_text.lower().replace(' ','_')}/{tahun_text}/json/{filename}'


                            try:
                                save_json = SaveJson(
                                    source='satu data kementrian lingkungan hidup dan kehutanan',
                                    country_name='Indonesia',
                                    level='Nasional',
                                    tags=['https://phl.menlhk.go.id', 'TABULAR', category_text, sub_category_text],
                                    path_data_raw=[path_data_raw],
                                    response=self.url_page,
                                    title='TABULAR',
                                    category=category_text,
                                    sub_category=sub_category_text,
                                    range_date=tahun_text,
                                    data=data
                                )
                                await save_json.save_json_local(filename, category_text.lower().replace(' ','_'), sub_category_text.lower().replace(' ','_'), tahun_text)
                            except Exception as e:
                                print(e)

                            if self.uploads3 == True:
                                try:
                                    await upload_to_s3(f'data/{category_text.lower().replace(' ','_')}/{sub_category_text.lower().replace(' ','_')}/{tahun_text}/{filename}', path_data_raw.replace('s3://',''))
                                    pass
                                except Exception as e:
                                    raise e

            except Exception as e:
                print(e)
            except TimeoutError:
                print('Timeout')
            finally:
                if browser:
                    await browser.close()




    async def close_banner(self, page):
        close_button = page.locator('//html/body/div[5]/div/div[6]/button[1]')

        if not await close_button.is_visible():
            pass
        else:
            await close_button.wait_for(timeout=10000)
            if await close_button.count() > 0:
                await close_button.click()



    async def _get_table_data(self, page):
        html_content = await page.content()
        sel = Selector(text=html_content)

        theads = sel.xpath('/html/body/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/div[2]/div/table/thead/tr/th/text()').getall()
        tbodys = sel.xpath('/html/body/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/div[2]/div/table/tbody/tr')
        tfoots = sel.xpath('/html/body/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/div[2]/div/table/tfoot/tr')


        headers = [header.strip().lower() for header in theads]

        data = []

        for tbody in tbodys:
            cells = tbody.xpath('./td/text()').getall()
            cells = [cell.strip() for cell in cells]
            if len(cells) == len(headers):
                row_dict = dict(zip(headers, cells))
                data.append(row_dict)
                


        for tfoot in tfoots:
            cells = tfoot.xpath('./td/text()').getall()
            cells = [cell.strip() for cell in cells]
            if len(cells) == len(headers):
                row_dict = dict(zip(headers, cells))
                data.append(row_dict)


        # # Print hasil
        # for item in data:
        #     print(item)

        # print(data)
        # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

        return data


