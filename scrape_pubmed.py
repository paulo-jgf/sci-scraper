# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 16:19:55 2021

Use o Firefox para descobrir os seletores que funcionam no requests!


@author: paulo
"""

import requests, bs4, re
from datetime import datetime
import pandas as pd 


# Pega as informações detalhadas de cada artigo
def detailArticle(X):
    global investigar
    if X['URL'] in detailed_urls:
        return ['zzz..' for i in range(8)]
    else:
        detailed_urls.append(X['URL'])
    
    print(X['URL'])
    res = requests.get(X['URL'])
    sopa = bs4.BeautifulSoup(res.text, 'html.parser')
    
    # Autores
    autores_compl, i = [], 1
    while i:
        autor = sopa.select(
                'div.authors-list:nth-child(1) > span:nth-child({}) > a:nth-child(1)'.format(i))
        if not autor: break
    
        # No authors listed
        if 'no author' in autor[0].text.lower():
            autores_compl.append('?')
        else:
            autores_compl.append(autor[0].text.strip())
        i+=1
    autores_compl = '; '.join(autores_compl)
    
    # DOI
    doi = sopa.select('#full-view-identifiers > li:nth-child(3) > span:nth-child(1) > a:nth-child(2)')
    if doi: doi = doi[0].text.strip().strip('.')       
    else: doi = '?'
    
    # PMCID e URL texto
    pmcid = sopa.select('#full-view-identifiers > li:nth-child(2) > span:nth-child(1) > a:nth-child(2)')
    if pmcid: 
        pmcid = pmcid[0].text.strip()
        
        # As vezes o PMCID não está aqui...
        if 'PMC' in pmcid:      
            url_fulltext = 'https://www.ncbi.nlm.nih.gov/pmc/articles/{}/'.format(pmcid)            
        else:
            # Pode ser que seja o DOI aqui...
            if doi == '?': doi = pmcid
            pmcid, url_fulltext = '?', '?'
            
    else: 
        pmcid, url_fulltext = '?', '?'
        
    # Abstract
    abstract = sopa.select('#enc-abstract > p:nth-child(1)')
    if abstract: abstract = abstract[0].text.strip()
    else: abstract = '?'
    
    # Keywords
    kw = sopa.select('#abstract > p:nth-child(3)')
    if kw: kw = kw[0].text.split(':')[1].strip()
    else: kw = '?'
    
    def prep_info_author(infoAuth, nameAuth):
        infoAuth = infoAuth[0].text.strip(' 0123456789')
        countryAuth = infoAuth.split(',')[-1].strip(' .')
        
        # Fora de padrao
        if len(countryAuth) > 65 and '@' not in countryAuth: countryAuth = countryAuth.split()[-1]
        
        # Email
        if '@' in countryAuth and len(countryAuth) < 75: countryAuth = countryAuth.split('.')[0].strip()
        
        # Tira termos numericos
        countryAuth = ' '.join([t for t in countryAuth.split() if not re.sub('\D','',t)]).strip()
        
        return {'nameAuth':nameAuth, infoAuth:'infoAuth', 'countryAuth':countryAuth}
    
    # Existem autores? Se sim, vamos buscar info do autor 1
    pais_autor1 = '?'
    infoAllauthors = []
    
    if len(autores_compl) > 1 and autores_compl[0] != '?':
        info_autor1 = sopa.select('div.affiliations:nth-child(1) > ul:nth-child(2) > li:nth-child(1)')
        
        if info_autor1:
            
            for ia in range(1, 1000):
                sel = 'div.affiliations:nth-child(1) > ul:nth-child(2) > li:nth-child({})'
                info_autorL = sopa.select(sel.format(ia))
                
                if not info_autorL:
                    info_autorL = sopa.select(sel.format(ia - 1))[0].text.strip(' 0123456789')
                    break
                else:
                    aux = prep_info_author(sopa.select(sel.format(ia)),
                                           autores_compl[ia-1])
                    infoAllauthors.append(aux)
            
            info_autor1 = info_autor1[0].text.strip(' 1')
            pais_autor1 = info_autor1.split(',')[-1].strip(' .')
            
            # Fora de padrao
            if len(pais_autor1) > 65 and '@' not in pais_autor1: pais_autor1 = pais_autor1.split()[-1]
            
            # Email
            if '@' in pais_autor1 and len(pais_autor1) < 75: pais_autor1 = pais_autor1.split('.')[0].strip()
            
            # Tira termos numericos
            pais_autor1 = ' '.join([t for t in pais_autor1.split() if not re.sub('\D','',t)]).strip()
            
        else:
            info_autorL = '?'
            info_autor1 = '?'
            investigar.append(X['URL'])
    else:
        info_autor1 = '?'
    
    print(autores_compl)
    #print(infoAllauthors)
        
    return autores_compl, pais_autor1, info_autor1, doi, pmcid, url_fulltext, abstract, kw

def trabalha_pagina_busca(sopa, nartigos, termos):
    global investigar
    investigar = []
    
    def separa_periodico_data(info_pub):
        info_pub = [t.strip() for t in info_pub.split('.')]
        periodico = info_pub[0]
        
        data = info_pub[1].split()
        ano, mes, dia = data[0], '?', '?'
        
        if len(data) > 1: mes = data[1]         
        if len(data) > 2: dia = data[2]
        
        return periodico, ano, mes, dia
    
    # Time stamp prep
    dt = str(datetime.now())[:-7]
    
    def layerOneExtract():
        # Title, url ID (PMID)
        el1 = sopa.select(
        'article.full-docsum:nth-child({}) > div:nth-child(2) > div:nth-child(1) > a:nth-child(1)'.format(
                        na))
        # Authors shorts
        el2 = sopa.select(
        'article.full-docsum:nth-child({}) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > span:nth-child(1)'.format(
                        na))
        # Complete cite
        el3 = sopa.select(
        'article.full-docsum:nth-child({}) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > span:nth-child(3)'.format(
                        na))[0].text.strip()
        
        # Article type
        el4 = sopa.select(
        'article.full-docsum:nth-child({}) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > span:nth-child(7)'.format(
                        na))
        
        # Trabalhando a cita completa para tirar periodico e a data, caso normal
        if ';' in el3:
            periodico, ano, mes, dia = separa_periodico_data(info_pub=el3.split(';')[0].strip())
            if 'ahead of print' in el3:
                investigar.append(el3)
                ahead_print = 'Y'
            else:
                ahead_print = 'N'
        # From complete cite to get periodic, date, and ahead of print info
        else:
            periodico, ano, mes, dia = separa_periodico_data(info_pub=el3.split(':')[0].strip())
            if 'ahead of print' in el3:
                ahead_print = 'Y'
            else:
                investigar.append(el3)
                ahead_print = 'N'
        
        if el4: 
            el4 = el4[0].text.strip(' .')
        else: 
            el4 = '?' 
        
        
        artData = {  
                     'DT': dt, # time stamp
                     'TITLE':el1[0].text.strip(),
                     'PMID': el1[0]['href'].strip('/'),
                     'TIPO_ARTIGO':el4,
                     'AUTORES_CITACAO':el2[0].text.strip(),
                     'PERIODICO':periodico,
                     'ANO':ano,
                     'MES':mes,
                     'DIA':dia,
                     'AHEAD_PRINT': ahead_print,
                     'CITA_COMPLETA':el3,
                     'URL':'https://pubmed.ncbi.nlm.nih.gov'+el1[0]['href']
                     }

        return artData        
    
    perPageRes = []
    # Max results is 200 per page, as hard coded. Results selectors go from 2 to 201
    # na is the selector index
    for na in range(2, min(nartigos + 2, 202)):
        
        # IGNORE ALL
        # Colunas descritor este trecho pode dar problema se os conjuntos de busca forem
        # de tamanhos diferentes, na hora de gerar o df no fim
        #for j in range(len(termos)):
        #    dados_art['DESCRITOR_' + str(j)] = termos[j]
        
        try:
            perPageRes.append(layerOneExtract())
        except:
            # This error is not expected at all, so if it occurs one needs to implement a tracking method
            # as it is not inplace
            print('Err')
       
    return perPageRes


# Monte a página no navegador, com os filtros que quiser, e passe a url aqui, não mude opcao de paginacao ou numero de resultados exibidos              
def baixa_url_pre_montada(url):
    
    # Adiciona a op 200 por pagina e page=1
    res = requests.get(url + '&size=200&page=1')
    sopa = bs4.BeautifulSoup(res.text, 'html.parser')
    
    try:
        # Seletor pro elemento que contém o número de resultados, servirá para descobrir o npags a serem baixadas
        elem = sopa.select('.results-amount-container > div:nth-child(1) > span:nth-child(1)')
        nres = int( re.sub('\D','', elem[0].text.strip()) )
    except:
        # 0 resultados no par
        if 'No results were found' in res.text: print('0 resultados')
        else: print('Erro brabo')
        raise SystemExit
    
    print(nres, 'artigos localizados...')
    
    # Pega artigos da primeira página
    scrape_base = trabalha_pagina_busca(sopa, nres, termos=('ver url',))

    # Divide nresultados por 200, que é o n mostrado por página
    # Se tiver resto adiciona 1, se não tiver adiciona 0
    npags = int(nres / 200) + (nres % 200 > 0)
    
    # Se tiver mais que uma página, vamos explorar as demais páginas
    if npags > 1:
        for pag in range(2, npags + 1):
            print('pag', pag)
            
            # A página anterior já reduziu o número de artigos restantes em 200
            nres = nres - 200
            
            # Virando a pagina na url
            res = requests.get(url + '&size=200&page={}'.format(pag))
            sopa = bs4.BeautifulSoup(res.text, 'html.parser')
            
            # Pega artigos da página atual
            scrape_base = scrape_base + trabalha_pagina_busca(sopa, nres, termos=('ver url',))
                
    scrape_base = pd.DataFrame(scrape_base) 
    scrape_base.to_csv('scrape_base.csv', sep='|', index= False, encoding='utf-8')
            
    return scrape_base



# CITADO - quem cita o PMID 33303732
# https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid=33303732

def scrape_control(url='https://pubmed.ncbi.nlm.nih.gov/?term=target+trial+pregnancy+woman+saito', 
                   execFolder='tmp'):              
    global detailed_urls
    detailed_urls = []
    
    if execFolder: 
        if not execFolder.endswith('\\'): execFolder += '\\'    
    
    scrape_base = baixa_url_pre_montada(url)
    
    scrape_base.to_csv(execFolder + 'scrape_base_pub.csv', sep='|', index=False, encoding='utf-8')
    
    #
    df = scrape_base.copy()
    
    
    
    #autores_compl, doi, pmcid, url_fulltext, abstract, kw
    df['AUTOR_COMPLETO'], df['PAIS_AUTOR'], df['INFO_AUTOR_1'], df['DOI'], df['PMCID'], df['DOWNLOAD'], df['ABSTRACT'], df['KEYWORDS'] = zip(
            *df.apply(detailArticle, axis=1))
    
    df_scraped = df.copy()
    
    df = df[['DT', 'TITLE', 'TIPO_ARTIGO', 'PERIODICO', 'DIA', 'MES', 'ANO',
           'URL',  'AUTOR_COMPLETO', 'PAIS_AUTOR', 'INFO_AUTOR_1',
           'DOI', 'DOWNLOAD', 'ABSTRACT', 'KEYWORDS']]
    
    
    
    df['BASE'] = 'PUBMED'
    
    dup = df[df.duplicated(subset=['DOI'], keep=False)]
    
    #def limpa(x):
    #    if x == 'zzz..': return 'duplicata'
    #    return x
    #
    #df_final[['AUTOR_COMPLETO', 'PAIS_AUTOR', 'INFO_AUTOR_1','DOI', 'PMCID', 'ABSTRACT', 
    #          'KEYWORDS']] = df_final[['AUTOR_COMPLETO', 'PAIS_AUTOR', 'INFO_AUTOR_1','DOI', 'PMCID', 'DOWNLOAD', 'ABSTRACT', 
    #          'KEYWORDS']].applymap(limpa)
    
    with pd.ExcelWriter(execFolder + 'pubmed_complete.xlsx') as writer:
        df.to_excel(writer, sheet_name='results', index=False)
        
    return execFolder + 'pubmed_complete.xlsx'

if __name__ == "__main__":        
    scrape_control() 


