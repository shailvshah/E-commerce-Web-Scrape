# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 18:39:36 2020

@author: shail
"""

import pandas as pd


def review_manipulation():
    data_reviews = pd.read_excel('product_reviews.xlsx')
    data_reviews['Datetime'] = pd.to_datetime(data_reviews['Datetime'])
    data_reviews['Date'] = pd.to_datetime(data_reviews['Datetime']).dt.date
    data_reviews['Time'] = pd.to_datetime(data_reviews['Datetime']).dt.time
    data_reviews['RID'] = data_reviews['RID'].str.split('-').str[-1]
    data_reviews = data_reviews.sort_values(by=['Datetime'])
    data_reviews = data_reviews.drop(['Datetime'],axis=1)
    data_reviews = data_reviews.reset_index(drop=True)
    
    data_reviews = data_reviews[['SKUid','Date','Time','Review','Helpful','Unhelpful','RID']]
    
    return data_reviews