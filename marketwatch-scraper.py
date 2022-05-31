#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
from regex import P
import requests
import pandas as pd
from datetime import datetime
import numpy as np


class MarketWatchScraper:
    def __init__(self, ticker):
        self.ticker = ticker
    
    def __handle_exception__(self):
        print(f'Table could not be found with specified ticker: {self.ticker}. Please make sure this ticker is correct.')
        
    def get_news(self):
        r = requests.get(f'https://www.marketwatch.com/investing/stock/{self.ticker}?mod=search_symbol')
        soup = BeautifulSoup(r.text, 'html.parser')

        try:
            table = soup.findAll('div', class_= 'article__content')
        except Exception as e:
            if e.__class__ == AttributeError:
                self.handle_exception()
                raise
        
        text_arr = []
        href_arr = []
        timestamp_arr = []
        for x in table:
            try:
                text = x.find('a').text.replace('\n', '').strip()
                href = x.find('a').get('href')
                timestamp = x.find('div', class_= 'article__details').text.replace('\n', '')
                if 'a.m.' in timestamp:
                    loc = timestamp.find('a.m.')
                    timestamp = timestamp[:loc+3]
                    timestamp = datetime.strptime(timestamp, '%b. %d, %Y at %I:%M a.m').timestamp()
                elif 'p.m.' in timestamp:
                    loc = timestamp.find('p.m.')
                    timestamp = timestamp[:loc+3]
                    timestamp = datetime.strptime(timestamp, '%b. %d, %Y at %I:%M p.m').timestamp()

                text_arr.append(text)
                href_arr.append(href)
                timestamp_arr.append(timestamp)
            except:
                pass
            
        data = pd.DataFrame(zip(text_arr, href_arr, timestamp_arr), columns=['text', 'link', 'timestamp'])
        return data

    def get_key_data(self):
        r = requests.get(f'https://www.marketwatch.com/investing/stock/{self.ticker}?mod=search_symbol')
        soup = BeautifulSoup(r.text, 'html.parser')

        try:
            table = soup.find('ul', class_= 'list list--kv list--col50')
        except Exception as e:
            if e.__class__ == AttributeError:
                self.handle_exception()
                raise

        labels = []
        vals = []
        for x in table.findAll('li'):
            labels.append(x.find(class_='label').text)
            vals.append(x.find(class_='primary').text)

        data = pd.DataFrame(zip(labels, vals), columns = ['stat', 'val'])
        return data


    def get_competitors(self):
        r = requests.get(f'https://www.marketwatch.com/investing/stock/{self.ticker}?mod=search_symbol')
        soup = BeautifulSoup(r.text, 'html.parser')
        
        try:
            table = soup.find('tbody', class_='table__body')
        except Exception as e:
            if e.__class__ == AttributeError:
                self.handle_exception()
                raise
        
        company_names = []
        daily_changes = []
        market_caps = []
        for x in table.findAll('tr', class_='table__row'):
            company_names.append(x.find('td', class_='table__cell w50').text)
            daily_changes.append(x.find('td', class_='table__cell w25').text)
            market_caps.append(x.find('td', class_='table__cell w25 number').text)
        
        data = pd.DataFrame(zip(company_names, daily_changes, market_caps), columns = ['company', 'daily_change', 'market_cap'])
        return data

    def get_company_description(self):
        r = requests.get(f'https://www.marketwatch.com/investing/stock/{self.ticker}?mod=search_symbol')
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            return soup.find('div', class_='element element--description description__long').find('p').text
        except Exception as e:
            if e.__class__ == AttributeError:
                self.handle_exception()
                raise

    def get_profitability(self):
        r = requests.get(f'https://www.marketwatch.com/investing/stock/{self.ticker}/company-profile?mod=mw_quote_tab')
        soup = BeautifulSoup(r.text, 'html.parser')

        try:
            table = soup.find('table', class_='table value-pairs no-heading').findAll('tr', class_='table__row')
        except Exception as e:
            if e.__class__ == AttributeError:
                self.handle_exception()
                raise

        labels = []
        vals = []
        for x in table:
            labels.append(x.find('td', class_='table__cell w75').text)
            vals.append(x.find('td', class_='table__cell w25').text)

        data = pd.DataFrame(zip(labels, vals), columns = ['stat', 'val'])
        return data

    def get_insider_transactions(self):
        r = requests.get(f'https://www.marketwatch.com/investing/stock/{self.ticker}/company-profile?mod=mw_quote_tab')
        soup = BeautifulSoup(r.text, 'html.parser')

        try:
            table = soup.find('div', class_='insider-actions')
            table = table.find('table', class_='table table--secondary overflow--table align--left row-hover')
            table = table.find('tbody', class_='table__body')
        except Exception as e:
            if e.__class__ == AttributeError:
                self.handle_exception()
                raise
        
        res = []
        for i in table.findAll('td', class_='table__cell'):
            try:
                res.append(i.find('span', class_='primary').text)
            except:
                pass

        data = pd.DataFrame(np.array_split(res,len(res)/4), columns = ['date', 'shareholder', 'type', 'shares'])
        return data

    def get_upgrades_downgrades(self): 
        r = requests.get('https://www.marketwatch.com/tools/upgrades-downgrades?mod=mw_quote_upgrades')
        soup = BeautifulSoup(r.text, 'html.parser')

        table = soup.find('tbody', class_= 'table__body').findAll('tr', class_='table__row')
        res = []
        for i in table:
            for x in i.findAll('td'):
                res.append(x.text.replace('\n', ''))
        res = [i for i in res if i != '']

        data = pd.DataFrame(np.array_split(res,len(res)/5), columns = ['date', 'ticker', 'company_name', 'category', 'analyst_firm'])
        return data


    def get_analyst_snapshot(self):
        r = requests.get(f'https://www.marketwatch.com/investing/stock/{self.ticker}/analystestimates?mod=mw_quote_tab')
        soup = BeautifulSoup(r.text, 'html.parser')

        try:
            table = soup.find('table', class_='table value-pairs no-heading font--lato').find('tbody')
        except Exception as e:
            if e.__class__ == AttributeError:
                self.handle_exception()
                raise
            
        labels = []
        vals = []
        for x in table.findAll('tr', class_='table__row'):
            try:
                labels.append(i.find('td', class_= 'table__cell w75').text)
                vals.append(i.find('td', class_= 'table__cell w25').text)
            except:
                pass

        data = pd.DataFrame(zip(labels, vals), columns = ['stat', 'val'])
        return data

fn = MarketWatchScraper('aapl')

fn.get_analyst_snapshot()
fn.get_news()
fn.get_key_data()
fn.get_competitors()
fn.get_company_description()
fn.get_profitability()
fn.get_insider_transactions()
fn.get_upgrades_downgrades()
fn.get_analyst_snapshot()
