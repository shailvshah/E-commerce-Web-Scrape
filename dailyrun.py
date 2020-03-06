# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 13:49:19 2020

@author: shail
"""

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup  # HTML data structure
import requests
import re
from datetime import datetime

data = pd.read_excel('product_reviews.xlsx')