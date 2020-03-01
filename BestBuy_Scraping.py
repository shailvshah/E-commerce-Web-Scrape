# -*- coding: utf-8 -*-
"""
Created on Sun Feb 5 22:21:50 2020

@author: shail
"""

import pandas as pd
from bs4 import BeautifulSoup  # HTML data structure
import requests
import re
from datetime import datetime

#get product descriptions
def getTitles(soup):
    #finds all <h1> with class heading-5 v-fw-regular
    con = soup.findAll("h1", {"class":"heading-5 v-fw-regular"})                
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
        #split string on ':' and pull the last part
        modelno = modelno.split(":")[-1]
    return modelno


# get Current Price
def getCurrentPrice(soup):
    con = soup.findAll("div",{"class":"priceView-hero-price priceView-customer-price"})
     #check if field is empty
    if not con:                                                                
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
    #check if field is empty
    if not con:       
        #take current price                                                          
        price = getCurrentPrice(soup)
    else:
        for c in con:
            price = re.findall(r' \$\d+.+\d',str(c.text))                       
            price = re.findall(r'\d+.+\d',str(price))
            price = re.sub(r',','',str(price))
            
    return str(price)


#get All Ratings per product
def getRating_Count(soup):
    con = soup.findAll("div",{"class":"rating-bars-v2"})
    #check if field is empty
    if not con:                                                                 
            ratings_count = '0.0'
    else:
        for c in con:   
            ratings_count = c.text
     
    return ratings_count


#get individual product links!
def getProductLinks(soup, total_pages,page_url, header):
    productlinks = []
    if total_pages>1:
        for i in range(total_pages):
            i = i+1
            #first page is base url
            if i == 1:                                                          
                for container in soup.findAll('h4', {"class": "sku-header"}):
                    for c in container:
                        if c.get('href') == None:
                            continue
                        productlinks.append(c.get('href'))
            #base url changes!!!!
            else:                                                               
                page_url = 'https://www.bestbuy.com/site/tvs/65-inch-tvs/pcmcat1514910447059.c?cp='+str(i)+'&id=pcmcat1514910447059'
                html = requests.get(page_url, headers = header, timeout=5 )
                #create new soup object for new url and scrape
                soup = BeautifulSoup(html.content, 'html.parser')               
                for container in soup.findAll('h4', {"class": "sku-header"}):
                    for c in container:
                        if c.get('href') == None:
                            continue
                        productlinks.append(c.get('href'))
    #only 1 page!
    else:                                                                        
        for container in soup.findAll('h4', {"class": "sku-header"}):
            for c in container:
                if c.get('href') == None:
                    continue
                productlinks.append(c.get('href'))
    return productlinks


def getReviews(page_url,k,modelname,sid):
    reviews = []
    timestamp = []
    rid = []
    helpful = []
    unhelpful = []
    skuid = []    
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
    html = requests.get(page_url, headers = header)                 
    soup = BeautifulSoup(html.content, 'html.parser')
    
    print('\n\n\nWriting into reviews for product - ',k)
    con = soup.findAll("div", {"class":"reviews-pagination col-xs-4 col-lg-3"})
    for c in con:
        init = c.text
        tot_reviews = init.split(" ")[5]
        tot_reviews = re.sub(r',','',str(tot_reviews))
        tot_reviews = int(tot_reviews)
        r_icount = re.findall(r'-\d+',c.text)
        r_icount = re.findall(r'\d+',str(r_icount))
        r_icount = int(*r_icount)
    print('\nNo. of reviews in product '+str(k)+' are '+str(tot_reviews))
    if tot_reviews<=r_icount:
        r_tot_pages = 1
    else:
        if tot_reviews%r_icount == 0:
            r_tot_pages = tot_reviews//r_icount
        else:
            r_tot_pages = (tot_reviews//r_icount)+1
            
    if r_tot_pages>1:
        j=tot_reviews
        for i in range(r_tot_pages):
            
            #first page is base url
            
            if i == 0:
                #print('Page - '+str(i+1)+' of '+str(r_tot_pages))
                con = soup.findAll("div", {"class":"ugc-review-body body-copy-lg"})
                for c in con:
                    reviews.append(c.text)
                    rid.append(modelname+'-'+str(j))
                    skuid.append(sid)
                    j-=1
                con = soup.findAll("div",{"class":"review-context"})
                for c in con:
                    timestamp.append(c.time['title'])
                con = soup.findAll("button",{"class":"btn btn-outline btn-sm helpfulness-button no-margin-l"})
                for c in con:
                    dummy = c.text
                    dummy = dummy.split(' ')[-1]
                    helpful.append(int(re.search(r'\d+',str(dummy)).group()))
                con = soup.findAll("button",{"class":"btn-default-link link neg-feedback"})
                for c in con:
                    dummy = c.text
                    dummy = dummy.split(' ')[-1]
                    unhelpful.append(int(re.search(r'\d+',str(dummy)).group()))
            else:
                #print('Page - '+str(i+1)+' of '+str(r_tot_pages))
                page_url_review = page_url+'&page='+str(i+1)
                html = requests.get(page_url_review, headers = header)
                #create new soup object for new url and scrape
                soup1 = BeautifulSoup(html.content, 'html.parser')
                con = soup1.findAll("div", {"class":"ugc-review-body body-copy-lg"})
                for c in con:
                    reviews.append(c.text)
                    rid.append(modelname+'-'+str(j))
                    skuid.append(sid)
                    j-=1
                con = soup1.findAll("div",{"class":"review-context"})
                for c in con:
                    timestamp.append(c.time['title'])
                con = soup1.findAll("button",{"class":"btn btn-outline btn-sm helpfulness-button no-margin-l"})
                for c in con:
                    dummy = c.text
                    dummy = dummy.split(' ')[-1]
                    helpful.append(int(re.search(r'\d+',str(dummy)).group()))
                con = soup1.findAll("button",{"class":"btn-default-link link neg-feedback"})
                for c in con:
                    dummy = c.text
                    dummy = dummy.split(' ')[-1]
                    unhelpful.append(int(re.search(r'\d+',str(dummy)).group()))
            i = i+1
    else:
        #print('Page - 1 of '+str(r_tot_pages))
        con = soup.findAll("div", {"class":"ugc-review-body body-copy-lg"})
        j=tot_reviews
        for c in con:
            reviews.append(c.text)
            rid.append(modelname+'-'+str(j))
            skuid.append(sid)
            j-=1
        con = soup.findAll("div",{"class":"review-context"})
        for c in con:
            timestamp.append(c.time['title'])
        con = soup.findAll("button",{"class":"btn btn-outline btn-sm helpfulness-button no-margin-l"})
        for c in con:
            dummy = c.text
            dummy = dummy.split(' ')[-1]
            helpful.append(int(re.search(r'\d+',str(dummy)).group()))
        con = soup.findAll("button",{"class":"btn-default-link link neg-feedback"})
        for c in con:
            dummy = c.text
            dummy = dummy.split(' ')[-1]
            unhelpful.append(int(re.search(r'\d+',str(dummy)).group()))
    
    print('\nGoing over next product....')
    product_review = pd.DataFrame(list(zip(skuid, timestamp, rid,reviews,helpful,unhelpful)),
                             columns =['SKUid','Datetime','RID','Review','Helpful','Unhelpful'])
    return product_review
    
        
        


def doTransform(currentprice, actualprice, ratings_count):
    star5 = []
    star4 = []
    star3 = []
    star2 = []
    star1 = []
    #helper for transformations of current and original price str into float
    removetable = str.maketrans('','','\'][')                                   
    for r in ratings_count:
        #if no reviews all stars will be 0.0
        if r == '0.0':                                                          
                star5.append('0')
                star4.append('0')
                star3.append('0')
                star2.append('0')
                star1.append('0')
        else:
            #individually assign rating count per #' stars
            for i in range(5):                                                  
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
    
    return currentprice,actualprice,star5,star4,star3,star2,star1
    

        
        
   

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
        if ratings_count[i-1] == '0.0':
            print('No Reviews Found!')
            productreview = pd.DataFrame(columns =['SKUid','Datetime','RID','Review','Helpful','Unhelpful'])
            productreview.to_excel("reviews_"+skuid[i-1]+str(datetime.date(datetime.now()))+".xlsx") 
        else:
            page_url_review = product[:5]+'/reviews/'+product[6:]
            page_url_review = page_url_review.split('.')[0]
            page_url_review = 'https://www.bestbuy.com/'+str(page_url_review)+'?variant=A&sort=MOST_RECENT'
            productreview = getReviews(page_url_review,i,modelno[i-1],skuid[i-1])
            productreview.to_excel("reviews_"+skuid[i-1]+str(datetime.date(datetime.now()))+".xlsx") 
        i+=1
        
        
    #transform the result from above to further push into data frame for future manipulations!
    currentprice,actualprice,star5,star4,star3,star2,star1 = doTransform(currentprice,actualprice,ratings_count)
 
   
    #create dataframe
    product_description = pd.DataFrame(list(zip(skuid, titles, modelno)),
                             columns =['SKUid','Item Descrption','ModelNo'])
    product_info = pd.DataFrame(list(zip(skuid,todaydate,star1,star2,star3,star4,star5,currentprice,actualprice)),
                                columns = ['SKUid','Date','1 star','2 stars','3 stars','4 stars','5 stars','Current Price','Original Price'])
    
    product_description.to_excel("product_description_"+str(datetime.date(datetime.now()))+".xlsx")
    
    product_info.to_excel("product_info_"+str(datetime.date(datetime.now()))+".xlsx")
    
    

    
    
    
  
        
    
    
    
            

    
            
        
    