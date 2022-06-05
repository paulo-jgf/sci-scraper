# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 15:25:49 2022

This module calls the individual scrapers and combines the results. If more scrapers are to be added this
module will need to be updated

@author: paulo
"""

import os
import pandas as pd
import scrape_pubmed
import scrape_scidirect

def init(config):
    
    # Creating the exec folder
    execFolder = 'tmp'
    os.makedirs(execFolder, exist_ok=True)
    results_path = []
    
    if config['url_query_pubmed']:
        path = scrape_pubmed.scrape_control(url=config['url_query_pubmed'],
                                            execFolder=execFolder)        
        # returned string with file path
        results_path.append(path)
        
    if config['url_query_science_direct']:
        path = scrape_scidirect.scrape_control(url=config['url_query_science_direct'],
                                            execFolder=execFolder)                
        # returned string with file path
        results_path.append(path)
    
    config['results_path'] = results_path
    

def combine_results(config):
    
    def reader(path):
        return pd.read_excel(path, sheet_name = 'results', dtype=str)
    
    # Reading and concatanating results from scrapers
    df = pd.concat( [ reader(path) for path in config['results_path'] ] )
    
    df.drop_duplicates(subset=['DOI'], keep='first', inplace=True)

    # If there are required terms, we will apply em to all papers found
    if config['required_terms']:
        required_terms_logic(config, df)

    
    with pd.ExcelWriter('Final result.xlsx') as writer:
        df.to_excel(writer, sheet_name='combined_result', index=False)   
    

# You may update or chenge this logic
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









