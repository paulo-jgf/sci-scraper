# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 15:20:18 2022

@author: paulo
"""

import assistant

# Paste the url between the quotation marks
url_query_pubmed = ''

# Paste the url between the quotation marks
url_queri_science_direct = ''

# Fill the terms that are required to be either in the keywords, title or abstract
# Fill beetween the quotation marks. Split the terms with commas as in the example
required_terms = 'Term1, term2'

# Dont edit from here
assistant.init(config = {'url_query_pubmed':url_query_pubmed,
                         'url_query_science_direct':url_queri_science_direct,
                         'required_terms':required_terms})

