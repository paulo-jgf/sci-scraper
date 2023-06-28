# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 15:25:49 2022

This module calls the individual scrapers and combines the results. If more scrapers are to be added this
module will need to be updated

@author: paulo
"""

import pandas as pd
import scrape_pubmed
import scrape_scidirect
import scraped_processing

def init(config):
    
    if config['url_query_pubmed']:
        resPubmed = scrape_pubmed.scrape_control(url=config['url_query_pubmed'])
        
    if config['url_query_science_direct']:
        resSciDirect = scrape_scidirect.scrape_control(url=config['url_query_science_direct'])
    
    df = scraped_processing.main()
    
    if config['required_terms']:
        df = required_terms_logic(config, df)
    
    df.to_excel('Final result.xlsx', sheet_name='combined_result', index=False)
    
    return {'df':df,
            'resPubmed':resPubmed,
            'resSciDirect':resSciDirect}
    

# You may update or change this logic
# Separate with , to form a group of any words that should be in
# Separete with ; to form a group of group of required any words that should be in
# Fields to be searched are: TITLE, ABSTRACT, KEYWORDS
def required_terms_logic(config, df, columns=['TITLE', 'ABSTRACT', 'KEYWORDS']):
    
    if ';' in config['required_terms']:
        required_groups = config['required_terms'].split(';')
        
        required_groups = [list_strip(grp.split(',')) for grp in required_groups]
    
    else:
        required_groups = [list_strip( config['required_terms'].split(',') ) ]
    
    terms_query = '('+') AND ('.join([' OR '.join(grp) for grp in required_groups]) +')'
    print('FYI filter query to combined results:', terms_query)
    
    def filter_applier(X, columns=columns):
        text = ' '.join(X[col] for col in columns)
        
        for grp in required_groups:
            grp_ok = False
            for term in grp:
                if term in text:
                    grp_ok = True
                    break
            if not grp_ok:
                return False
            
        return True
    
    return df[df.apply(filter_applier, axis=1)]
                
        
def list_strip(lis):
    return [st.strip() for st in lis]









