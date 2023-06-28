# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 15:20:18 2022

If you dont want to scrape one of available bases just leave an empty string at its url, or 0 value, or None value

@author: paulo
"""

import assistant

# Paste the url between the quotation marks
#url_query_pubmed = 'https://pubmed.ncbi.nlm.nih.gov/?term=target+trial+pregnancy+woman+saito'
url_query_pubmed = """https://pubmed.ncbi.nlm.nih.gov/?term=%28%28%28%22target+trial%22%5BAll+Fields%5D++OR+%22target+trial+emulation%22%5BAll+Fields%5D%29++OR+%28%22non-randomised+trial+emulation%22+%5BAll+Fields%5D%29++OR+%28%22hypothetic+trial%22%5BAll+Fields%5D++OR+%22hypothetical+trial%22%5BAll+Fields%5D%29%29++AND++%28%28%22Preconception+Care%22%5BMesh%5D++OR+%22Preconception%22%5BAll+Fields%5D%29++OR+%28%22Pregnancy%22%5BMesh%5D++OR+%22Pregnancy%22%5BAll+Fields%5D++OR+%22Pregnan*%22%5BAll+Fields%5D%29++OR+%28%22Perinatal+Care%22%5BMesh%5D++OR+%22Perinatal%22%5BAll+Fields%5D%29++OR+%28%22Postpartum+Period%22%5BMesh%5D++OR+%22Postpartum+Period%22%5BAll+Fields%5D++OR+%22Postpartum%22%5BAll+Fields%5D++OR+%22Puerperium%22%5BAll+Fields%5D%29++OR+%22lactation%22%5BAll+Fields%5D%29%29%29&size=200"""

# Paste the url between the quotation marks
#url_queri_science_direct = 'https://www.sciencedirect.com/search?tak=%28Nanomedicines%20OR%20Nanocomposites%20OR%20Nanoparticles%20OR%20Nanostructures%20OR%20Nanotechnology%29%20AND%20%28COVID-19%20OR%20coronavirus%20OR%20SARS-CoV-2%29&qs=target%20trial%20pregnancy%20woman'
url_queri_science_direct = """https://www.sciencedirect.com/search?qs=%28%22target%20trial%22%20OR%20%22non-randomised%20trial%20emulation%22%20OR%20%22hypothetic%3F%3F%20trial%22%29%20%20AND%20%20%28Preconception%20%20OR%20Pregnan%3F%3F%20%20OR%20Perinatal%20%20OR%20Postpartum%20OR%20Puerperium%20OR%20lactation%29"""

# Fill the terms that are required to be either in the keywords, title or abstract
# Fill beetween the quotation marks. Split the terms with commas as in the example
# EXAMPLE: required_terms = 'virus; corona, covid'
required_terms = ''

# DONT EDIT FROM HERE


res = assistant.init(config = {'url_query_pubmed':url_query_pubmed,
                               'url_query_science_direct':url_queri_science_direct,
                               'required_terms':required_terms})



#Acrescentar nome auto info author1




