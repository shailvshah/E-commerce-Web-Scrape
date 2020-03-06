# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 13:49:19 2020

@author: shail
"""

import pandas as pd
from bs4 import BeautifulSoup  # HTML data structure
import requests
import re
from datetime import datetime
from BestBuy_Scraping import getProductLinks,getTitles,getSKUID,getModelNo,getCurrentPrice,getOriginalPrice,getRating_Count,doTransform,getReviews






if __name__ == "__main__":
    page_url = 'https://www.bestbuy.com/site/tvs/65-inch-tvs/pcmcat1514910447059.c?id=pcmcat1514910447059'
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
    html = requests.get(page_url, headers = header, timeout=5 )                 #timeouts argument can be avoided!
        
    soup = BeautifulSoup(html.content, 'html.parser')
    print('Starting to Scrape base URL...')
    
    #calc. total no. of items per page
    con = soup.findAll("div", {"class":"left-side"})
    for c in con:
        pcount = re.findall(r'-\d+',c.text)
        pcount = re.findall(r'\d+',str(pcount))
        pcount = int(*pcount)
    
    #calc total items for product category
    conn = soup.findAll("div", {"class":"banner-middle-column"})
    for c in conn:
        icount = re.findall(r'\d+',c.text)
        icount = int(*icount)
    
    print('Items found under product category - ',icount)
    #calc total no of pages.
    if icount<=pcount:
        total_pages = 1
    else:    
    
        if icount%pcount==0:
            total_pages = icount//pcount
        else:
            total_pages = icount//pcount+1
    print('Total no. of pages to scrape - ',total_pages)
    #store product links
    
    print('\n\n\n################### Extracting Product Links #######################')
    productlinks = getProductLinks(soup,total_pages,page_url,header)            
    
 
    titles = []
    skuid = []
    modelno = []
    currentprice = []
    actualprice = []
    ratings_count = []
    todaydate = []
    #find all details per product one by one!
    i=1
    print('\n\n\n################# Scraping Individual Products Content ################### ')
    for product in productlinks:                                                
        page_url = 'https://www.bestbuy.com/'+str(product)
        html = requests.get(page_url, headers = header)
        soup1 = BeautifulSoup(html.content, 'html.parser')
        titles.append(getTitles(soup1))
        skuid.append(getSKUID(soup1))
        modelno.append(getModelNo(soup1))
        ratings_count.append(getRating_Count(soup1))
        currentprice.append(getCurrentPrice(soup1))
        actualprice.append(getOriginalPrice(soup1))
        todaydate.append(datetime.date(datetime.now()))
        
    #transform the result from above to further push into data frame for future manipulations!
    currentprice,actualprice,star5,star4,star3,star2,star1 = doTransform(currentprice,actualprice,ratings_count)
 
   
    #create dataframe
    product_description = pd.DataFrame(list(zip(skuid, titles, modelno)),
                             columns =['SKUid','Item Descrption','ModelNo'])
    product_info = pd.DataFrame(list(zip(skuid,todaydate,star1,star2,star3,star4,star5,currentprice,actualprice)),
                                columns = ['SKUid','Date','1 star','2 stars','3 stars','4 stars','5 stars','Current Price','Original Price'])
    
    product_description.to_excel("product_description.xlsx")
    with pd.ExcelWriter('product_info.xlsx',mode='a') as writer:  
        product_info.to_excel(writer)
        
        
"""     WIP - Reviews format and manipulation still lil tricky... especially storing RID number and appending on count 
    i=1
    productreview = pd.DataFrame(columns=['SKUid','Datetime','RID','Review','Helpful','Unhelpful'])
    print('\n\n\n################# Scraping and appending reviews  ################### ')
    for product in productlinks:                                                
        page_url = 'https://www.bestbuy.com/'+str(product)
        html = requests.get(page_url, headers = header)
        soup1 = BeautifulSoup(html.content, 'html.parser')
        titles.append(getTitles(soup1))
        skuid.append(getSKUID(soup1))
        modelno.append(getModelNo(soup1))
        ratings_count.append(getRating_Count(soup1))
        if ratings_count[i-1] != 0:
            page_url_review = product[:5]+'/reviews/'+product[6:]
            page_url_review = page_url_review.split('.')[0]
            page_url_review = 'https://www.bestbuy.com/'+str(page_url_review)
            productreview.append(getReviews(page_url_review,i,modelno[i-1],skuid[i-1]))
        else:
            continue 
        i+=1
    productreview['Datetime'] = pd.to_datetime(data_reviews['Datetime'])
    productreview['Date'] = pd.to_datetime(productreview['Datetime']).dt.date
    productreview['Time'] = pd.to_datetime(productreview['Datetime']).dt.time
    productreview['RID'] = data_reviews['RID'].str.split('-').str[-1]
    productreview = productreview.sort_values(by=['Datetime'])
    productreview = productreview.drop(['Datetime'],axis=1)
    productreview = productreview.reset_index(drop=True)
    
    with pd.ExcelWriter('reviews.xlsx',mode='a') as writer:  
        product_info.to_excel(writer) 
"""    
    