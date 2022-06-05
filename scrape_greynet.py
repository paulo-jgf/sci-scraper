# -*- coding: utf-8 -*-
"""
Created on Mon May  2 18:03:28 2022

Just a proof of concept

@author: paulo
"""

import requests

url = "http://greyguiderep.isti.cnr.it/simplesearchloc.php"
txt = "bale" # Simple term search

form_data = {"azione": "SimpleSearch",
             "collection": "ALL",
             "param": txt,
             "langver": "en"}

# construct the POST request
with requests.session() as s:

    r = s.post(url, data=form_data)


























