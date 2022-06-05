# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 15:20:18 2022

@author: paulo
"""

import assistant

# Paste the url between the quotation marks
url_query_pubmed = 'https://pubmed.ncbi.nlm.nih.gov/?term=target+trial+pregnancy+woman+saito'

# Paste the url between the quotation marks
url_queri_science_direct = 'https://www.sciencedirect.com/search?tak=%28Nanomedicines%20OR%20Nanocomposites%20OR%20Nanoparticles%20OR%20Nanostructures%20OR%20Nanotechnology%29%20AND%20%28COVID-19%20OR%20coronavirus%20OR%20SARS-CoV-2%29&qs=target%20trial%20pregnancy%20woman'

# Fill the terms that are required to be either in the keywords, title or abstract
# Fill beetween the quotation marks. Split the terms with commas as in the example
# EXAMPLE: required_terms = 'virus; corona, covid'
required_terms = ''

# DONT EDIT FROM HERE


assistant.init(config = {'url_query_pubmed':url_query_pubmed,
                         'url_query_science_direct':url_queri_science_direct,
                         'required_terms':required_terms})

