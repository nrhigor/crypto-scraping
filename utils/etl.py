import os
import pandas as pd

from datetime import datetime as dt
from dotmap import DotMap
from logging import Logger

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CoinGeckoETL:
    def __init__(self, logger: Logger, url: str, paths: DotMap):
        self.logger = logger
        self.url    = url
        self.paths  = paths

        service = ChromeService(self.paths.chromedriver)
        options = webdriver.ChromeOptions()
        options.binary_location = self.paths.chrome

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
    
    def run_etl(self, quantity_of_coins: int = 50):
        TABLE_XPATH = '/html/body/div[2]/main/div/div[5]/table'

        try:
            self.logger.info('> Accessing CoinGecko...')
            self.driver.get(self.url)
            self.logger.info('')

            columns = list()
            data    = list()

            self.logger.info('> Retriving headers...')
            headers_obj = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, f'{TABLE_XPATH}/thead')), message='The website was unreachable.')
            headers     = headers_obj.text.split(' ')[1:]

            columns.extend(headers[:5])
            columns[1] = f'{columns[1]} (in $)'
            columns.append(f'{headers[5]} {headers[6]} (in $)')
            columns.append(f'{headers[7]} {headers[8]} (in $)')
            columns.insert(1, 'Acronym')

            self.logger.info('> Headers retrieved!')
            self.logger.info('')

            self.logger.info(f'> Now, retriving the first {quantity_of_coins} coins...')

            for row_index in range(1, quantity_of_coins+1):
                row_xpath = f'{TABLE_XPATH}/tbody/tr[{row_index}]'
                coin_row  = self.driver.find_element(By.XPATH, row_xpath)

                row_data = coin_row.text.split('\n')
                coin, acronym = row_data.pop(1).rsplit(' ', 1)
                row_data.insert(1, acronym)
                row_data.insert(1, coin)
                row_data.remove('Buy')

                last_item = row_data.pop(-1)
                values = [item.replace(',', '').replace('.', '').replace('$', '') if '%' not in item else item for item in last_item.split(' ')]

                row_data.extend(values)

                PERCENTAGE_POSITIONS = (4, 5, 6)
                for position in PERCENTAGE_POSITIONS:
                    signals_xpath = f'{row_xpath}/td[{position+3}]/span[1]'
                    class_name = self.driver.find_element(By.XPATH, signals_xpath).get_dom_attribute('class')

                    signal = '+' if class_name == 'gecko-up' else '-'
                    row_data[position] = f'{signal}{row_data[position]}'

                data.append(row_data[1:])

            self.logger.info('> Coins retrieved!')
            self.logger.info('')

            self.logger.info('> Saving file with retrieved coins...')

            df = pd.DataFrame(data, columns=columns, index=[i for i in range(1, len(data)+1)])

            df['Price (in $)']      = df['Price (in $)'].astype('Float64')
            df['24h Volume (in $)'] = df['24h Volume (in $)'].astype('Float64')
            df['Market Cap (in $)'] = df['Market Cap (in $)'].astype('Float64')

            filename = f'Top_{quantity_of_coins}_Coins_{dt.today().strftime("%Y-%m-%d")}.xlsx'
            filepath = os.path.join(self.paths.output, filename)
            df.to_excel(filepath)

            if not os.path.exists(filepath): raise FileNotFoundError(f'{filename} not created.')

            self.logger.info('> Filed saved!')
            self.logger.info('')

        except Exception as e:
            self.logger.error('')
            self.logger.error(e)
            self.logger.error('')
        finally:
            self.driver.quit()

