# -*- coding: utf-8 -*-
"""
Created on Jun 01 16:19:55 2023


@author: paulo
"""

import requests
import bs4
import re
import shelve
from datetime import datetime

#import sys
#if sys.getrecursionlimit() < 6000:
#    sys.setrecursionlimit(6000)

# Mount the page in the browser, with the filters you want, and pass the url here, do not change the pagination option or the number of results displayed              
def getPubMedUrl(url):
    
    # Set show size and page
    res = requests.get(url + '&size=200&page=1')
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    
    try:
        # Get n results to solve n pages
        resultsCount = soup.find('div', {'class': 'results-amount-container'})
        nres = int( re.sub('\D','', resultsCount.text.strip()) )
    except:
        # 0 results
        if 'No results were found' in res.text:
            print('0 results')
        else:
            print('Fatal error')
        raise SystemExit
    
    print(nres, 'found articles...')
        
    ResultPages = []
    # Get 1st page results
    ResultPages.append({
                        'pageNum': 1,
                        'timeStamp': str(datetime.now())[:-7],
                        'pageHtml': res.text,
                        'pageArticles': searchPageWorker(soup),
                        'query': url + '&size=200&page=1'
                        })

    # Solving n pages
    npags = int(nres / 200) + (nres % 200 > 0)
    
    # Page control
    for pag in range(2, npags + 1):
               
        res = requests.get(url + '&size=200&page={}'.format(pag))
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        ResultPages.append({
                            'pageNum': pag,
                            'timeStamp': str(datetime.now())[:-7],
                            'pageHtml': res.text,
                            'pageArticles': searchPageWorker(soup),
                            'query': url + '&size=200&page={}'.format(pag)
                            })
            
    return ResultPages

def searchPageWorker(soup):
    
    #listedArticles = soup.find_all('a', {'class': 'docsum-title'})
    listedArticles = soup.find_all('div', {'class': 'docsum-content'})
    
    urlForm = 'https://pubmed.ncbi.nlm.nih.gov{}'
    
    pageArticles =[]
    
    for div in listedArticles:
        
        title_a = div.find('a', {'class': 'docsum-title'})
        
        pageArticles.append(
                            {                   
                             'id': title_a['href'].strip('/'),
                             'title': title_a.text.strip(),
                             'url': urlForm.format(title_a['href']),
                             'articleResumedHtml': str(div),
                             'articleFullHtml': None,
                             'citedBy': 'W.I.P.'
                            }
                           )
       
    return pageArticles

def getArticlesUrl(ResultPagesRich):
    
    for page in ResultPagesRich:
        
        for article in page['pageArticles']:
            print(article['url'])
            res = requests.get( article['url'] )
            status = res.status_code
            
            if status != 200:
                print('Erro carregamento:', article['url'])
                article['articleFullHtml'] = str(status)
                article['articleSideHtml'] = str(status)
            else:
                soup = bs4.BeautifulSoup(res.text, 'html.parser')
                articleMain = soup.find('main', {'class': 'article-details'})
                article['articleFullHtml'] = str(articleMain)
                
                articleSideHtml = soup.find('aside', {'class': 'page-sidebar'})
                article['articleSideHtml'] = str(articleSideHtml)
    
    return ResultPagesRich


def getWhoCites(ResultPagesRich):
    
    for page in ResultPagesRich:
        
        for article in page['pageArticles']:            
            urlForm = 'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid={}'
            urlCy = urlForm.format(article['id'])
            article['citedBy'] = getPubMedUrl(urlCy)   
    
    return ResultPagesRich

#def modResultsPages(ResultPages):
#    
#    for page in ResultPages:
#        page['timeStamp'] = str(datetime.now())[:-7]

def scrape_control(url):
    
    def dbUpdateData():
        db = shelve.open('scraped_db')
        temp = {'scrapeDate':scrapeDate, 
                'scrapeSource':scrapeSource,
                'scrapedData':ResultPages}      
        db[scrapeId] = temp   
        db.close()        
        

    # Databse prep
    scrapeDate = str(datetime.now())[:-7].split()[0]
    scrapeSource = 'pubmed'
    
    db = shelve.open('scraped_db')
    entries = list(db.keys())

    if not entries: 
        scrapeId = '0'
    else:
        scrapeId = str( max([int(scrapeId) for scrapeId in entries]) + 1)  
    db.close()
    
    # Outer layer scrape   
    ResultPages = getPubMedUrl(url)
    
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
    
    # TODO CITADOs
    #ResultPages = getWhoCites(ResultPages)
    
    return {'scrapeDate':scrapeDate, 
            'scrapeSource':scrapeSource,
            'scrapedData':ResultPages} 
    
if __name__ == "__main__":        
    url = """https://pubmed.ncbi.nlm.nih.gov/?term=%28%28%28%22target+trial%22%5BAll+Fields%5D++OR+%22target+trial+emulation%22%5BAll+Fields%5D%29++OR+%28%22non-randomised+trial+emulation%22+%5BAll+Fields%5D%29++OR+%28%22hypothetic+trial%22%5BAll+Fields%5D++OR+%22hypothetical+trial%22%5BAll+Fields%5D%29%29++AND++%28%28%22Preconception+Care%22%5BMesh%5D++OR+%22Preconception%22%5BAll+Fields%5D%29++OR+%28%22Pregnancy%22%5BMesh%5D++OR+%22Pregnancy%22%5BAll+Fields%5D++OR+%22Pregnan*%22%5BAll+Fields%5D%29++OR+%28%22Perinatal+Care%22%5BMesh%5D++OR+%22Perinatal%22%5BAll+Fields%5D%29++OR+%28%22Postpartum+Period%22%5BMesh%5D++OR+%22Postpartum+Period%22%5BAll+Fields%5D++OR+%22Postpartum%22%5BAll+Fields%5D++OR+%22Puerperium%22%5BAll+Fields%5D%29++OR+%22lactation%22%5BAll+Fields%5D%29%29%29"""
    resPubmed = scrape_control(url)


#    ResultPages = getPubMedUrl(url)
#    ResultPages = getArticlesUrl(ResultPages)