# -*- coding: utf-8 -*-
"""
Created on Sat Jun 10 08:48:52 2023

All the scraped data will be dealt with here to prepare the output

@author: paulo
"""

import bs4
import shelve
import pandas as pd
import re
import calendar

noDoi = 0

def processScrapedData():

    scrapedBases = LookUpRecentData()
    articles = []
    
    for base in scrapedBases.keys():
        
        if base == 'pubmed':
            articles = articles + pubmedWorker(scrapedBases['pubmed']['scrapedData'])
            
        
        elif base == 'scridirect':
            articles = articles + scidirectWorker(scrapedBases['scridirect']['scrapedData'])
        
        else:
            print('Alert! Processing logic not defined for scraped database:', base)
            
    return pd.DataFrame(articles)


def LookUpRecentData():

    db = shelve.open('scraped_db')
    entries = list(db.keys())
    
    # Which bases were explored?
    scrapedBases = {}
    
    for entry in entries:
        
        if db[entry]['scrapeSource'] in scrapedBases.keys():        
            scrapedBases[db[entry]['scrapeSource']].append(int(entry))
            
        else:
            scrapedBases[db[entry]['scrapeSource']] = [int(entry)]
    
    # Get most recent scrape stored
    for source in scrapedBases.keys():
        print('Source:', source, '| Selected:', max( scrapedBases[source] ))
        scrapedBases[source] = db[ str(max( scrapedBases[source] )) ]
    
    db.close()
    return scrapedBases


def pubmedWorker(scrapedData, base):
    global noDoi
    
    def getPeriodicDate(resumeCite):
        try:
            info_pub = [t.strip() for t in resumeCite.split('.')]       
            data = info_pub[1].split()
            y, m, d = data[0], '?', '?'
            
            if len(data) > 1: 
                m = data[1].split(';')[0]    
            if len(data) > 2: 
                d = data[2].split(';')[0]
                d = re.sub('\D','', d)
                if not d:
                    d = '?'
            
        except:
            y, m, d = '?', '?', '?'
            
        return {'y': y, 'm': m, 'd': d}
    

    dt = scrapedData[0]['timeStamp']
    
    processedArticles = []
    
    for page in scrapedData:
        
        for article in page['pageArticles']:
            artResumedSoup = bs4.BeautifulSoup(article['articleResumedHtml'], 'html.parser')
            artFullSoup = bs4.BeautifulSoup(article['articleFullHtml'], 'html.parser')
            artSideSoup = bs4.BeautifulSoup(article['articleSideHtml'], 'html.parser')
            
            resumeCite = artResumedSoup.find('span', {'class': 'docsum-journal-citation full-journal-citation'}).text
            
            periodic = artFullSoup.find('button', {'class': 'journal-actions-trigger trigger'})
            if periodic:
                periodic = periodic['title'].strip()
            else:
                periodic = resumeCite
            
            pDate = getPeriodicDate(resumeCite)
            
            authorComplete = artResumedSoup.find('span', {'class': 'docsum-authors full-authors'}).text
            
            authors = artFullSoup.find_all('span', {'class': 'authors-list-item'})
            #author1Name = authors[0].find('a', {'class': 'full-name'}).text
            author1Affliations = [ a['title'] for a in authors[0].find_all('a', {'class': 'affiliation-link'}) ]
            
            author1Country = '?'
            if author1Affliations:
                author1Country = author1Affliations[0].split(',')[-1].strip('.- ')
                if '@' in author1Country:
                    author1Country = author1Country.split('.')[0].strip()
                    
                countryProblems = (
                        False,
                        len(re.sub('\D','',author1Country)) > 0
                                  )
                if any(countryProblems):
                    author1Country = '?'
            else:
                author1Affliations = '?'
                           
            doi = artFullSoup.find('a', {'data-ga-action': 'DOI'})
            
            if doi:
                doi = doi.text.strip()
            else:
                noDoi += 1
                doi = 'NA - {}'.format(noDoi)
            
            #abstract = artFullSoup.find('div', {'class': 'abstract-content selected'}).get_text(separator=' ')
            abstract = artFullSoup.find('div', {'class': 'abstract-content selected'}).text
            abstract = '\n'.join([p.strip() for p in abstract.split('\n') if p.strip()])
            
            downloadUrls = artSideSoup.find('div', {'class': 'full-text-links-list'})
            downloadUrls = '\n ; \n'.join( [a['href'] for a in downloadUrls.find_all('a')] )
            
            processedArticles.append(
                    {
                    'DT': dt,
                    'TITLE': article['title'].strip(),
                    'PERIODIC': periodic,
                    'YEAR': pDate['y'],
                    'MONTH': pDate['m'],
                    'DAY': pDate['d'],
                    'URL': article['url'],
                    'AUTHOR_COMPLETE': authorComplete,
                    'AUTHOR_COUNTRY': author1Country,
                    'AUTHOR_1_INFO': '; '.join(author1Affliations),
                    'DOI': doi,
                    'DOWNLOAD': downloadUrls,
                    'ABSTRACT': abstract,
                    'BASE': base.upper()
                    }
                    )
            
    return processedArticles   


def scidirectWorker(scrapedData, base):
    global noDoi
    months = [m for m in list(calendar.month_name) if m]
    
    def getPeriodicDate(dt_sep):       
         
        # Solving day, month and year
        dt_sep = dt_sep.split()
        y, m, d = '?', '?', '?'
        
        if dt_sep and len(re.sub('\D','', dt_sep[-1])) == 4:
            y = dt_sep[-1]
            
            if len(dt_sep) > 1 and dt_sep[-2] in months:
                m = dt_sep[-2][:3]
                
                if len(dt_sep) > 2:
                    d = re.sub('\D','', dt_sep[-3])
                    
        return {'y': y, 'm': m, 'd': d}

    dt = scrapedData[0]['timeStamp']
    
    processedArticles = []

    for page in scrapedData:
        
        for article in page['pageArticles']:
            
            artResumedSoup = bs4.BeautifulSoup(article['articleResumedHtml'], 'html.parser')
            artFullSoup = bs4.BeautifulSoup(article['articleFullHtml'], 'html.parser')
            artSideSoup = bs4.BeautifulSoup(article['articleSideHtml'], 'html.parser')
            
            #periodic = artFullSoup.find('a', {'class': 'anchor publication-title-link anchor-navigation'}).text
            
            resumeCite = artResumedSoup.find('span', {'class': 'srctitle-date-fields'})
            resumeCite = [span.text for span in resumeCite.find_all('span')]
            
            periodic = resumeCite[0]
            pDate = getPeriodicDate(resumeCite[-1])
            
            doi = artFullSoup.find('a', {'class': 'anchor doi anchor-default anchor-external-link'})
            if doi:
                doi = doi.text    
                if doi.startswith('https://doi.org/'):
                    doi = doi[16:]
            else:
                noDoi += 1
                doi = 'NA - {}'.format(noDoi)
                        
            abstract = artFullSoup.find('div', {'class': 'abstract author'})
            if abstract:
                abstract = abstract.get_text(separator=' ')
                if abstract[:8].lower() == 'abstract':
                    abstract = abstract[8:].strip()
                
            else:
                abstract = '?'
                print('abstract fail:', article['url'])

            authorComplete = artFullSoup.find('div', {'class': 'author-group'})
            authorComplete = authorComplete.find_all('span', {'class': 'react-xocs-alternative-link'})
            authorComplete = [no.text.strip() for no in authorComplete]
            if authorComplete:
                authorComplete = ', '.join(authorComplete) + '.'
            else:
                authorComplete = '?'
            
            
            author1Affliations = artSideSoup.find('div', {'class': 'affiliation'})
            if author1Affliations:
                author1Affliations = author1Affliations.text
                #author1Country = author1Affliations.split(',')[-1].strip('.- ')
                author1Country = author1Affliations.split(';')[0].split(',')[-1].strip('.- ')
            else:
                author1Affliations = '?'
                author1Country = '?'

            processedArticles.append(
                    {
                    'DT': dt,
                    'TITLE': article['title'].strip(),
                    'PERIODIC': periodic,
                    'YEAR': pDate['y'],
                    'MONTH': pDate['m'],
                    'DAY': pDate['d'],
                    'URL': article['url'],
                    'AUTHOR_COMPLETE': authorComplete,
                    'AUTHOR_COUNTRY': author1Country,
                    'AUTHOR_1_INFO': author1Affliations,                    
                    'DOI': doi,
                    'ABSTRACT': abstract,
                    'DOWNLOAD': article['url'],
                    'BASE': base.upper()
                    }
                    )
            
    
    return processedArticles


def main():
    scrapedBases = LookUpRecentData()    
    processedArticles = pubmedWorker(scrapedBases['pubmed']['scrapedData'], base='pubmed')    
    processedArticles2 = scidirectWorker(scrapedBases['scidirect']['scrapedData'], base='scidirect')
    df = pd.DataFrame(processedArticles + processedArticles2)
    df.drop_duplicates(subset=['DOI'], keep='first', inplace=True)
    return df

if __name__ == "__main__":
    
    scrapedBases = LookUpRecentData()
    
    processedArticles = pubmedWorker(scrapedBases['pubmed']['scrapedData'], base='pubmed')
    
    processedArticles2 = scidirectWorker(scrapedBases['scidirect']['scrapedData'], base='scidirect')
    
    df = pd.DataFrame(processedArticles + processedArticles2)
    
    dff = df.drop_duplicates(subset=['DOI'], keep='first').copy()



















