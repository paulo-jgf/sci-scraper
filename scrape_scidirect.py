# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 08:25:25 2021

@author: paulo
"""


from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import pandas as pd
import re
import time
import json
import os
import calendar


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
def cozinha_elemento(seletor, timeout=60):
    global driver
    tentativa = 0
    
    if timeout == 0: max_tentativas = 1
    else: max_tentativas = timeout * 2
    
    # Time ut control
    while tentativa < max_tentativas:
        
        try:
            return driver.find_element_by_css_selector(seletor)
        except:
            tentativa += 1            
        
        if timeout > 0: time.sleep(0.5)
            
    return False

# Wait for specific term on html
def espera_termo_na_pagina(termo, testa_erro=False):
    global driver
    tentativa = 0
    
    # Error evidence check. Is it present?
    if testa_erro:
        # Pausa necessária para esperar livrar o último erro que ocorreu!
        time.sleep(1.0)
        if testa_erro in driver.page_source: return False     
    
    # Main loading test
    while termo not in driver.page_source:
        tentativa += 1
        time.sleep(0.5)

        # Error evidence check. Is it present? 
        if testa_erro:
            if testa_erro in driver.page_source: return False        
        
        # Timeout 20 s
        if tentativa > 120:
            print('Timeout: Loading > 60 seg')
            driver.quit()
            raise SystemExit
            
    return True

def busca_por_pagina():
    months = [m for m in list(calendar.month_name) if m]
    
    # timestamping!
    dt = str(datetime.now())[:-7]     
    
    # content elements
    elements = driver.find_elements_by_class_name('result-item-content')
    
    artigos = []
    
    # Iter found articles at current page
    for el_ex in elements:
    
        art_atual = {'DT': dt,
                     'TITLE':'',
                     'URL':'',
                     'PERIODICO':'',
                     'DATA_ARTIGO':'',
                     'DIA':'',
                     'MES':'',
                     'ANO':'',
                     'TIPO_ARTIGO':'',
                     'ACESSO_ART':'',
                     'DOWNLOAD':''}
        
        # Iter each article specfic information
        for e in el_ex.find_elements_by_tag_name("a"):
            
            eurl, eclass = e.get_attribute('href'), e.get_attribute('class')
            
            if eurl:
                if 'result-list-title-link' in eclass:
                    art_atual['TITLE'] = e.text
                    art_atual['URL'] = eurl
                elif 'subtype-srctitle-link' in eclass:
                    art_atual['PERIODICO'] = e.text
                elif 'download-link' in eclass:
                    art_atual['DOWNLOAD'] = eurl
                    
        # Iter to find article date
        for e in el_ex.find_elements_by_class_name("srctitle-date-fields"):
                
            # Solving day, month and year
            dt_sep = re.sub('AVAILABLE ONLINE ', '', e.text).split()[-3:]
            
            if dt_sep and len(re.sub('\D','', dt_sep[-1])) == 4:
                art_atual['ANO'] = dt_sep[-1]
                
                if len(dt_sep) > 1 and dt_sep[-2] in months:
                    art_atual['MES'] = dt_sep[-2]
                    
                    if len(dt_sep) > 2:
                        art_atual['DIA'] = re.sub('\D','', dt_sep[-3])
                        
            art_atual['DATA_ARTIGO'] = art_atual['DIA'] +' '+ art_atual['MES'] +' '+ art_atual['ANO']
            break
            
        # Iter to find article type and access level
        for e in el_ex.find_elements_by_tag_name("span"):
            eclass = e.get_attribute('class')
            if eclass:
                if 'article-type' in eclass and not art_atual['TIPO_ARTIGO']:
                    art_atual['TIPO_ARTIGO'] = e.text
                    
                if 'access-label' in eclass and not art_atual['ACESSO_ART']:
                    art_atual['ACESSO_ART'] = e.text
    
        artigos.append(art_atual)
        
    return artigos


def itera_busca(url):
    global driver
    
    init_firefox()
    
    # Set show size
    if '&show=100' not in url: url += '&show=100'
    
    driver.get(url)
    # Wait for "order by date" to appear, to make sure page is properly loaded
    cozinha_elemento('div.ResultSortOptions:nth-child(3) > div:nth-child(1) > a:nth-child(3) > span:nth-child(1)')
       
    # Total results value
    el = driver.find_element_by_css_selector('#srp-facets > div:nth-child(1) > h1:nth-child(1) > span:nth-child(1)')
    nres = re.sub('\D','', el.text)
    
    if nres: nres = int(nres)
    else:
        print('A busca falhou no primeiro carregamento de pagina, o numero de resultados nao pode ser determinado!')
        raise SystemExit
    
    print(nres, 'artigos localizados...')
       
    # Solving number of pages
    npags = int(nres / 100) + (nres % 100 > 0)
    
    scrape_base, offset = [], 0
    
    for i in range(npags):
        
        # turn the page, in this case adding offset, for all pages after the first 
        if i > 0:
            offset += 100
            driver.get(url + '&offset='+ str(offset))
            # Vamos esperar o contador de páginas aparecer, para garantir que a página carregou
            espera_termo_na_pagina(termo='Page {} of {}'.format(str(i + 1), str(npags)))   
        
        print('Pagina carregada!')
        scrape_pag =  busca_por_pagina()
        print('Pagina',i+1,'n=',len(scrape_pag))
        
        scrape_base = scrape_base +scrape_pag
    
    scrape_base = pd.DataFrame(scrape_base)
    driver.quit()    
    return scrape_base
    

def scrape_avancado(df):
    global scrape_final, falhas, driver
    scrape_final, falhas, jsons = {}, {}, {}
    
    for i, row in df.iterrows():
        
        # Restart driver after 50 requests, to prevent memory overload
        if not i % 50:
            if i > 1: driver.quit()
            init_firefox()

        url = row['URL']
        
        # Already caught?
        if url in scrape_final.keys() and url not in falhas.keys(): continue
    
        falhou = ''
    
        print(url)
        
        driver.get(url)
        # Required pause
        time.sleep(3)
        
        try:
            chave_json = '<script type="application/json" data-iso-key="_0">'
            html = driver.page_source 
            # Json start <script type="application/json" data-iso-key="_0">
            # Json closure </script>
            info_json = html[html.find(chave_json) + len(chave_json):]
            info_json = info_json[:info_json.find('</script>')].strip()
            info_json = json.loads(info_json)
            
            jsons[url] = info_json.copy()
        except:
            falhou += '-json'
            
        try:
            # Here a "list" of abstracts, but e want author
            abstract = info_json['abstracts']['content']
            
            # Selecting the abstract (Pode ser author, highlights, graphical.. etc?)
            if len(abstract) == 1:
                abstract = abstract[0]['$']['id']
            else:
                # Precisamos ver qual é o que queremos!
                for ab in abstract:
                    if ab['$']['class'] == 'author':
                       abstract = ab['$']['id']
                       break
            
            # Opção texto feio, confiável.. mas inutil quase
            #abstract = str(abstract[0]['$$'])
            
            # parag selector, from within the json...          
            el = driver.find_element_by_css_selector('#'+abstract)      
            abstract = el.text
            
        except:
            abstract = '?'
            falhou += '-abs'
            
        try:           
            doi = info_json['article']['doi']
            #info_json['article']
        except:
            doi = '?'
            falhou += '-doi'
            
        
        try:
            grupo_autores = driver.find_elements_by_class_name('author-group')
            
            nomes = grupo_autores[0].find_elements_by_xpath('//span[@class="text given-name"]')
            sobrenomes = grupo_autores[0].find_elements_by_xpath('//span[@class="text surname"]')
            
            nomes_completos = [nomes[i].text +' '+ sobrenomes[i].text for i in range(len(nomes))]
            
            
            #afiliacao = driver.find_elements_by_xpath('//dl[@class="affiliation"]')  Não funciona
            #autores_list = info_json['authors']['content']
            #autores_list = info_json['authors']['content'][0]['$$']
            #autores_list = [a['$$'] for a in autores_list]
            #[1]['$$'][0]['_']
            
        except:
            nomes_completos = ['?']
            falhou += '-aut'
        
        # Info autor 1 affiliation
        try:
            # Expanding authors list to make it work
            el = driver.find_element_by_css_selector('#show-more-btn > span:nth-child(1)')
            el.click()
            time.sleep(0.5)
            
            # Option 2       
            #el = driver.find_element_by_css_selector('dl.affiliation:nth-child('+str(len(nomes_completos) + 2) +') > dd:nth-child(2)')
            #info_autor_1 = el.text
            
            # Op 1
            info_autor = driver.find_elements_by_xpath('//dl[@class="affiliation"]')
            if info_autor:
                info_autor = [a.text for a in info_autor if len(a.text.strip()) > 2]
            else:
                info_autor = '?'
            
        except:
            falhou += '-filiacao'
        
        try:
            kw = driver.find_elements_by_xpath('//div[@class="keyword"]')
            if kw:
                kw  = [k.text for k in kw if len(k.text) > 2]
            else:
                kw  = '?'
                
        except:
            falhou += '-kw'
            
        if falhou: falhas[url] = falhou
        
        scrape_final[url] = {
                'AUTOR_COMPLETO': nomes_completos,
                'INFO_AUTOR'    : info_autor,
                'DOI'           : doi,
                'ABSTRACT'      : abstract,
                'KEYWORDS'      : '; '.join(kw)}
    
    driver.quit()
    
    def to_df(scrape_final):
        df = []
        
        for key in scrape_final.keys():
            dic = scrape_final[key].copy()
            dic['URL'] = key
            df.append(dic)
            
        return pd.DataFrame(df)

    df_final = to_df(scrape_final)
    
    return jsons, df_final


def to_df(scrape_final):
    df = []
    
    
    for key in scrape_final.keys():
        dic = scrape_final[key].copy()
        
        info_aut = dic['INFO_AUTOR']        
        dic['INFO_AUTOR'] = [item for sublist in info_aut for item in sublist.split('\n') if len(item) > 1]
        
        info_aut1 = dic['INFO_AUTOR'][0].split()
        
        dic['INFO_AUTOR_1'] = ' '.join(info_aut1[:-1]).strip(' ,')
        dic['PAIS_AUTOR'] = info_aut1[-1]
                
        
        dic['URL'] = key
        df.append(dic)
        
    return pd.DataFrame(df)

def scrape_control(url = 'https://www.sciencedirect.com/search?tak=%28Nanomedicines%20OR%20Nanocomposites%20OR%20Nanoparticles%20OR%20Nanostructures%20OR%20Nanotechnology%29%20AND%20%28COVID-19%20OR%20coronavirus%20OR%20SARS-CoV-2%29&qs=target%20trial%20pregnancy%20woman', 
                   execFolder=''):

    if execFolder: 
        if not execFolder.endswith('\\'): execFolder += '\\'
            
    scrape_base = itera_busca(url)
    
    if os.path.exists(execFolder + 'scrape_base_scidirect.csv'):
        os.remove(execFolder + 'scrape_base_scidirect.csv')     
    
    scrape_base.to_csv(execFolder + 'scrape_base_scidirect.csv', sep='|', index=False, encoding='utf-8')
    
    scrape_base = pd.read_csv(execFolder + 'scrape_base_scidirect.csv', delimiter='|', encoding='utf-8', dtype=str).fillna('')
    
    jsons, df_final = scrape_avancado(scrape_base)
    
    df_final = to_df(scrape_final)
    
    df_final = scrape_base.merge(df_final, on='URL', how='outer')
    
    if os.path.exists(execFolder + 'scrape_quase_scidirect.csv'):
        os.remove(execFolder + 'scrape_quase_scidirect.csv')
    
    df_final.to_csv(execFolder + 'scrape_quase_scidirect.csv', sep='|', index=False, encoding='utf-8')
    
    resultado = df_final[['DT','TITLE', 'TIPO_ARTIGO', 'PERIODICO', 'DIA', 'MES', 'ANO',
           'URL',  'AUTOR_COMPLETO', 'PAIS_AUTOR', 'INFO_AUTOR_1',
           'DOI', 'DOWNLOAD', 'ABSTRACT', 'KEYWORDS']].copy()
    
    resultado['BASE'] = 'SCI.DIRECT'
    
    #dup = resultado[resultado.duplicated(subset=['DOI'], keep=False)]
    
    resultado['AUTOR_COMPLETO'] = resultado['AUTOR_COMPLETO'].apply(lambda x: '; '.join(x))    
    
    if os.path.exists(execFolder + 'scidirect_complete.xlsx'):
        os.remove(execFolder + 'scidirect_complete.xlsx')    
    
    with pd.ExcelWriter(execFolder + 'scidirect_complete.xlsx') as writer:
        resultado.to_excel(writer, sheet_name='results', index=False)
        
    return execFolder + 'scidirect_complete.xlsx'


if __name__ == "__main__":        
    scrape_control() 




# DEV TESTS
#init_firefox()
#
#
#driver.get('https://www.sciencedirect.com/science/article/pii/S1525001621002562')
#chave_json = '<script type="application/json" data-iso-key="_0">'
#html = driver.page_source 
#info_json = html[html.find(chave_json) + len(chave_json):]
#info_json = info_json[:info_json.find('</script>')].strip()
#info_json = json.loads(info_json)
#
## abre Json <script type="application/json" data-iso-key="_0">
## Fecha Json </script>
#
## [0]['$$'][1]['$$'][0]['_'] isso nunca funcionaria pois a estrutra de colchete em java não é nested como no python
#abstract = info_json['abstracts']['content']
#
##abstract = abstract[0]['$$'] errado
#
## Seletor do paragrafo, obtido de dentro do json...
#abstract = abstract[0]['$']['id']
#el = driver.find_element_by_css_selector('#'+abstract)
#el.text


#
#doi = info_json['article']['doi']
##info_json['article']
#
#grupo_autores = driver.find_elements_by_class_name('author-group')
#
#nomes = grupo_autores[0].find_elements_by_xpath('//span[@class="text given-name"]')
#sobrenomes = grupo_autores[0].find_elements_by_xpath('//span[@class="text surname"]')
#
#nomes_completos = [nomes[i].text +' '+ sobrenomes[i].text for i in range(len(nomes))]




