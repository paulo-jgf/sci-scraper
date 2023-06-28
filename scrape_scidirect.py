# -*- coding: utf-8 -*-
"""
Created on Jun 01 08:25:25 2023

@author: paulo
"""


from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from datetime import datetime

import re
import time
import bs4
import shelve

#import sys
#if sys.getrecursionlimit() < 6000:
#    sys.setrecursionlimit(6000)

# Automated browser init
def init_firefox(dir_princ='', esconder_janela=True):
    global driver
    
    options = Options()
    options.headless = esconder_janela

    profile = webdriver.FirefoxProfile()
    profile.set_preference('dom.disable_beforeunload', True)
    
    if dir_princ: dir_princ += '\\'
    
    # geckodriver expected to be in the same folder
    try:
        driver = webdriver.Firefox(options=options, executable_path=dir_princ+'geckodriver.exe')
    except:
        path_geckodriver = r'C:\Users\paulo\Desktop\Python\Drivers\geckodriver.exe'
        try:
            driver = webdriver.Firefox(options=options, executable_path=path_geckodriver)
        except:
            print('Copy a compatible geckodriver.exe to the folder where this module is')
            print('Download at https://github.com/mozilla/geckodriver/releases')
            raise SystemExit
            
# wait for required element to be loaded
def waitElementByXpath(xpathString, timeout=60):
    tryCount = 0    
    maxTries = max(timeout, 1)
    
    # Time ut control
    while tryCount < maxTries:
        
        try:
            return driver.find_element_by_xpath(xpathString)
        except:
            tryCount += 1            
        
        time.sleep(1)
    
    print('timeout')        
    return False

# Wait for specific term on html
def waitString(reqTerm, badTerm=False, timeout=60):
    tryCount = 0
    
    # Error evidence check. Is it present?
    if badTerm:
        # Pausa necessária para esperar livrar o último erro que ocorreu!
        time.sleep(1.0)
        if badTerm in driver.page_source: 
            return False     
    
    # Main loading test
    while reqTerm not in driver.page_source:
        tryCount += 1
        time.sleep(1)

        # Error evidence check. Is it present? 
        if badTerm:
            if badTerm in driver.page_source: 
                return False        
        
        # Timeout 20 s
        if tryCount > timeout:
            return False
            
    return True


def getSciDirectUrl(url):
    global driver
    
    init_firefox()
    
    # Set show size
    if '&show=100' not in url: url += '&show=100'
    
    driver.get(url)
    # Wait for "order by date" to appear, to make sure page is properly loaded
    waitElementByXpath("//div[contains(@class, 'ResultsFound')]")
        
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, 'html.parser')
    
    try:
        # Get n results to solve n pages
        resultsCount = soup.find('div', {'class': 'ResultsFound'})
        nres = int( re.sub('\D','', resultsCount.text.strip()) )
    except:
        # TODO get this right for sci direct, text is from pubmed
        if 'No results found.' in html:
            print('0 results')
        else:
            print('Fatal error')
        raise SystemExit
    
    print(nres, 'found articles...')
       
    # Solving number of pages
    npags = int(nres / 100) + (nres % 100 > 0)
    
    ResultPages = []
    offset = 0
    
    for iPag in range(npags):
        
        # turn the page, in this case adding offset, for all pages after the first 
        if iPag > 0:
            offset += 100
            driver.get(url + '&offset='+ str(offset))
            # Vamos esperar o contador de páginas aparecer, para garantir que a página carregou
            waitString(termo='Page {} of {}'.format(str(iPag + 1), str(npags)))   
        
        print('Page loaded!')
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')

        ResultPages.append({
                            'pageNum': iPag + 1,
                            'timeStamp': str(datetime.now())[:-7],
                            'pageHtml': html,
                            'pageArticles': searchPageWorker(soup),
                            'query': url + '&offset='+ str(offset)
                            })        

    driver.quit()    
    return ResultPages
    
def searchPageWorker(soup):
    
    #listedArticles = soup.find_all('a', {'class': 'docsum-title'})
    listedArticles = soup.find_all('div', {'class': 'result-item-content'})
    
    urlForm = 'https://www.sciencedirect.com{}'
    
    pageArticles =[]
    
    for div in listedArticles:
        
        title_a = div.find('a', {'class': 'anchor result-list-title-link u-font-serif text-s anchor-default'})
        
        pageArticles.append(
                            {                   
                             'id': title_a['href'].split('/')[-1],
                             'title': title_a.text.strip(),
                             'url': urlForm.format(title_a['href']),
                             'articleResumedHtml': str(div),
                             'articleFullHtml': None,
                             'citedBy': 'W.I.P.'
                            }
                           )
       
    return pageArticles

def getArticlesUrl(ResultPagesRich):
    global driver
    i = 0
    init_firefox()
    
    time.sleep(3)
    for page in ResultPagesRich:
        
        for article in page['pageArticles']:
            i += 1
                
            # Restart driver after 50 requests, to prevent memory overload
            if not i % 50:
                driver.quit()
                init_firefox()

            url = article['url']
            print(url)
            # Required pause
            driver.get(url)
            time.sleep(3)
            waitElementByXpath("//div[contains(@class, 'Article')]")
                       
            html = driver.page_source
            soup = bs4.BeautifulSoup(html, 'html.parser')
            
            #articleMain = soup.find('article', {'role': 'main'})
            articleMain = soup.find('div', {'class': 'Article'})
            
            if not articleMain:
                raise SystemExit
            
            article['articleFullHtml'] = str(articleMain)

            try:
                #el = driver.find_element_by_css_selector('#show-more-btn > span:nth-child(1)')
                el = driver.find_element_by_css_selector('button.workspace-trigger:nth-child(2) > span:nth-child(1)')
                el.click()
                el.click()
                
                waitElementByXpath("//div[contains(@class, 'Workspace text-s')]")
                
                html2 = driver.page_source
                soup2 = bs4.BeautifulSoup(html2, 'html.parser')              
                
                articleSideHtml = soup2.find('div', {'class': 'Workspace text-s'}) 
                article['articleSideHtml'] = str(articleSideHtml)
                
            except:
                article['articleSideHtml'] = ''
      
    driver.quit()
    
    return ResultPagesRich


#url = 'https://www.sciencedirect.com/search?tak=%28Nanomedicines%20OR%20Nanocomposites%20OR%20Nanoparticles%20OR%20Nanostructures%20OR%20Nanotechnology%29%20AND%20%28COVID-19%20OR%20coronavirus%20OR%20SARS-CoV-2%29&qs=target%20trial%20pregnancy%20woman'
def scrape_control(url = """https://www.sciencedirect.com/search?qs=%28%22target%20trial%22%20OR%20%22non-randomised%20trial%20emulation%22%20OR%20%22hypothetic%3F%3F%20trial%22%29%20%20AND%20%20%28Preconception%20%20OR%20Pregnan%3F%3F%20%20OR%20Perinatal%20%20OR%20Postpartum%20OR%20Puerperium%20OR%20lactation%29""" 
                   ):

    def dbUpdateData():
        db = shelve.open('scraped_db')
        temp = {'scrapeDate':scrapeDate, 
                'scrapeSource':scrapeSource,
                'scrapedData':ResultPages}      
        db[scrapeId] = temp   
        db.close()        
        

    # Databse prep
    scrapeDate = str(datetime.now())[:-7].split()[0]
    scrapeSource = 'scidirect'
    
    db = shelve.open('scraped_db')
    entries = list(db.keys())

    if not entries: 
        scrapeId = '0'
    else:
        scrapeId = str( max([int(scrapeId) for scrapeId in entries]) + 1)  
    db.close()
    
    # Outer layer scrape   
    ResultPages = getSciDirectUrl(url)
    
    # Saving partial data
    try:
        dbUpdateData()
    except:
        print('Failed db write:', scrapeSource)

    # Inner layer scrape
    ResultPages = getArticlesUrl(ResultPages)
    
    # Saving complete data
    try:
        dbUpdateData()
    except:
        print('Failed db write:', scrapeSource)
    
    return {'scrapeDate':scrapeDate, 
            'scrapeSource':scrapeSource,
            'scrapedData':ResultPages} 


if __name__ == "__main__":
    url = """https://www.sciencedirect.com/search?qs=%28%22target%20trial%22%20OR%20%22non-randomised%20trial%20emulation%22%20OR%20%22hypothetic%3F%3F%20trial%22%29%20%20AND%20%20%28Preconception%20%20OR%20Pregnan%3F%3F%20%20OR%20Perinatal%20%20OR%20Postpartum%20OR%20Puerperium%20OR%20lactation%29"""      
    resScidirect = scrape_control(url)






