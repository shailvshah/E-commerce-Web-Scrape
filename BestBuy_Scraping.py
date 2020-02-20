# -*- coding: utf-8 -*-
"""
Created on Sun Feb 5 22:21:50 2020

@author: shail
"""

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup  # HTML data structure
import urllib.request
import requests
import re


#get product descriptions
def getTitles(soup):
    con = soup.findAll("h1", {"class":"heading-5 v-fw-regular"})                #finds all <h1> with class heading-5 v-fw-regular
    for c in con:
        titles = c.text
    
    return titles

#get SKU id
def getSKUID(soup):
    con = soup.findAll("span", {"class":"product-data-value body-copy"})
    for c in con:
        skuid = c.text
    
    return skuid

# get Model no.
def getModelNo(soup):
    con = soup.findAll("div",{"class":"model product-data"})
    for c in con:
        modelno = c.text
        modelno = modelno.split(":")[-1]
    return modelno


# get Current Price
def getCurrentPrice(soup):
    con = soup.findAll("div",{"class":"priceView-hero-price priceView-customer-price"})
    
    if not con:                                                                 #check if field is empty
        price = '0.0'
    else:
        for c in con:   
            price = re.findall(r' \$\d+.+\d',str(c.text))
            price = re.findall(r'\d+.+\d',str(price))
            price = re.sub(r',','',str(price))
     
    return str(price)


# get Original Price
def getOriginalPrice(soup):
    con = soup.findAll("div",{"class":"pricing-price__regular-price sr-only"})
    if not con:                                                                 #check if field is empty
        price = '0.0'
    else:
        for c in con:
            price = re.findall(r' \$\d+.+\d',str(c.text))                       
            price = re.findall(r'\d+.+\d',str(price))
            price = re.sub(r',','',str(price))
            
    return str(price)


#get All Ratings per product
def getRating_Count(soup):
    con = soup.findAll("div",{"class":"rating-bars-v2"})
    
    if not con:                                                                 #check if field is empty
            ratings_count = '0.0'
    else:
        for c in con:   
            ratings_count = c.text
     
    return ratings_count

'''
def getRatingsReviewers(soup):
    conn = soup.findAll("div", {"class":"c-ratings-reviews-v2 ugc-ratings-reviews v-small"})
    ratings = []
    n_reviewers = []
    for con in conn:
        
         demo_soup = BeautifulSoup(str(con),'html.parser')
         match = demo_soup.get_text()
         ratings.append(re.findall(r' [\d]\.[\d] +',str(match)))
         demo = str(con.findAll("span", {"class":"c-total-reviews"}))
         match = demo_soup.get_text()
         dummy = re.findall(r'\(\d+,?\d+\)',str(match))
         n_reviewers.append(re.findall(r'\d+,?\d+',str(dummy))) 
    del(dummy)
    return(ratings,n_reviewers)
'''

#get individual product links!
def getProductLinks(soup, total_pages,page_url, header):
    productlinks = []
    if total_pages>1:
        for i in range(total_pages):
            i = i+1
            if i == 1:                                                          #first page is base url
                for container in soup.findAll('h4', {"class": "sku-header"}):
                    for c in container:
                        productlinks.append(c.get('href'))
            else:                                                               #base url changes!!!!
                page_url = 'https://www.bestbuy.com/site/tvs/65-inch-tvs/pcmcat1514910447059.c?cp='+str(i)+'&id=pcmcat1514910447059'
                html = requests.get(page_url, headers = header, timeout=5 )
    
                soup = BeautifulSoup(html.content, 'html.parser')               #create new soup object for new url and scrape
                for container in soup.findAll('h4', {"class": "sku-header"}):
                    for c in container:
                        productlinks.append(c.get('href'))
    else:                                                                       #only 1 page! 
        for container in soup.findAll('h4', {"class": "sku-header"}):
            for c in container:
                productlinks.append(c.get('href'))
    return productlinks


        
        
    

if __name__ == "__main__":
    page_url = 'https://www.bestbuy.com/site/tvs/65-inch-tvs/pcmcat1514910447059.c?id=pcmcat1514910447059'
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
    html = requests.get(page_url, headers = header, timeout=5 )                 #timeouts argument can be avoided!
    total_pages = 1
    
    soup = BeautifulSoup(html.content, 'html.parser')
    
    #calc. total no. of items
    con = soup.findAll("div", {"class":"left-side"})
    for c in con:
        pcount = re.findall(r'-\d+',c.text)
        pcount = re.findall(r'\d+',str(pcount))
        pcount = int(*pcount)
    
    #calc total no. of pages!
    conn = soup.findAll("div", {"class":"banner-middle-column"})
    for c in conn:
        icount = re.findall(r'\d+',c.text)
        icount = int(*icount)
    total_pages = (icount//pcount)+1
    
    productlinks = getProductLinks(soup,total_pages,page_url,header)            #store product links
    
    removetable = str.maketrans('','','\'][')                                   #helper for transformations of current and original price str into float

    titles = []
    skuid = []
    modelno = []
    currentprice = []
    actualprice = []
    ratings_count = []
    for product in productlinks:                                                #find all details per product one by one!
        page_url = 'https://www.bestbuy.com/'+str(product)
        html = requests.get(page_url, headers = header)
        soup = BeautifulSoup(html.content, 'html.parser')
        titles.append(getTitles(soup))
        skuid.append(getSKUID(soup))
        modelno.append(getModelNo(soup))
        ratings_count.append(getRating_Count(soup))
        currentprice.append(getCurrentPrice(soup))
        actualprice.append(getOriginalPrice(soup))
        
                
            
    
    #transform the result from above to further push into data frame for future manipulations!
    star5 = []
    star4 = []
    star3 = []
    star2 = []
    star1 = []
    for r in ratings_count:
        if r == '0.0':                                                          #if no reviews all stars will be 0.0
                star5.append('0')
                star4.append('0')
                star3.append('0')
                star2.append('0')
                star1.append('0')
        else:
            for i in range(5):                                                  #individually assign rating count per #' stars
                i=i+1
            
                if i == 1:
                    dummy = r.split(".")[i]
                    star5.append(dummy.split(" ")[1])
                elif i == 2:
                    dummy = r.split(".")[i]
                    star4.append(dummy.split(" ")[1])
                elif i == 3:
                    dummy = r.split(".")[i]
                    star3.append(dummy.split(" ")[1])
                elif i == 4:
                    dummy = r.split(".")[i]
                    star2.append(dummy.split(" ")[1])
                elif i == 5:
                    dummy = r.split(".")[i]
                    star1.append(dummy.split(" ")[1])
    for i in range(icount):
        star5[i] = re.sub(',','',str(star5[i]))
        star5[i] = int(star5[i])
        star4[i] = re.sub(',','',str(star4[i]))
        star4[i] = int(star4[i])
        star3[i] = re.sub(',','',str(star3[i]))
        star3[i] = int(star3[i])
        star2[i] = re.sub(',','',str(star2[i]))
        star2[i] = int(star2[i])
        star1[i] = re.sub(',','',str(star1[i]))
        star1[i] = int(star1[i])
        
    
    currentprice = [s.translate(removetable) for s in currentprice]
    currentprice = [float(i) for i in currentprice]
    actualprice = [s.translate(removetable) for s in actualprice]
    actualprice = [float(i) for i in actualprice]   
            

    
            
        
    