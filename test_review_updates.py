#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 20:26:35 2020

@author: shail
"""

import pandas as pd
from bs4 import BeautifulSoup  # HTML data structure
import requests
import re
from datetime import datetime
from BestBuy_Scraping import getProductLinks,getTitles,getSKUID,getModelNo,getTotalReviewsCount
from openpyxl import load_workbook



def getReviews(page_url,k,modelname,sid,reviewcount,r_tot_pages,tot_reviews):
        reviews = []
        timestamp = []
        rid = []
        helpful = []
        unhelpful = []
        skuid = []   
        
        header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
        html = requests.get(page_url, headers = header, timeout=5 )                 #timeouts argument can be avoided!
        soup = BeautifulSoup(html.content, 'html.parser')       
        if r_tot_pages>1:
            rc = ts = h = uh = reviewcount #count to scrape only new reviews
            j=tot_reviews
            for i in range(r_tot_pages):
                
                #first page is base url
                
                if i == 0:
                    #print('Page - '+str(i+1)+' of '+str(r_tot_pages))
                    con = soup.findAll("div", {"class":"ugc-review-body body-copy-lg"})
                    for c in con:
                        reviews.append(c.text)
                        rid.append(j)
                        skuid.append(sid)
                        j-=1
                        rc-=1
                    con = soup.findAll("div",{"class":"review-context"})
                    for c in con:
                        timestamp.append(c.time['title'])
                        ts-=1
                    con = soup.findAll("button",{"class":"btn btn-outline btn-sm helpfulness-button no-margin-l"})
                    for c in con:
                        dummy = c.text
                        dummy = dummy.split(' ')[-1]
                        helpful.append(int(re.search(r'\d+',str(dummy)).group()))
                        h-=1
                    con = soup.findAll("button",{"class":"btn-default-link link neg-feedback"})
                    for c in con:
                        dummy = c.text
                        dummy = dummy.split(' ')[-1]
                        unhelpful.append(int(re.search(r'\d+',str(dummy)).group()))
                        uh-=1
                else:
                    #print('Page - '+str(i+1)+' of '+str(r_tot_pages))
                    page_url_review = page_url+'&page='+str(i+1)
                    html = requests.get(page_url_review, headers = header)
                    #create new soup object for new url and scrape
                    soup1 = BeautifulSoup(html.content, 'html.parser')
                    con = soup1.findAll("div", {"class":"ugc-review-body body-copy-lg"})
                    for c in con:
                        if rc>=1:
                            reviews.append(c.text)
                            rid.append(j)
                            skuid.append(sid)
                            j-=1
                        else:
                            break
                        rc-=1
                    con = soup1.findAll("div",{"class":"review-context"})
                    for c in con:
                        if ts>=1:
                            timestamp.append(c.time['title'])
                        else:
                            break
                        ts-=1
                    con = soup1.findAll("button",{"class":"btn btn-outline btn-sm helpfulness-button no-margin-l"})
                    for c in con:
                        if h>=1:
                            dummy = c.text
                            dummy = dummy.split(' ')[-1]
                            helpful.append(int(re.search(r'\d+',str(dummy)).group()))
                        else:
                            break
                        h-=1
                    con = soup1.findAll("button",{"class":"btn-default-link link neg-feedback"})
                    for c in con:
                        if uh>=1:
                            dummy = c.text
                            dummy = dummy.split(' ')[-1]
                            unhelpful.append(int(re.search(r'\d+',str(dummy)).group()))
                        else:
                            break
                        uh-=1
                i = i+1
        else:
            rc = ts = h = uh = reviewcount 
            con = soup.findAll("div", {"class":"ugc-review-body body-copy-lg"})
            j=tot_reviews
            for c in con:
                if rc>=1:
                    reviews.append(c.text)
                    rid.append(j)
                    skuid.append(sid)
                    j-=1
                else:
                    break
                rc-=1
            con = soup.findAll("div",{"class":"review-context"})
            for c in con:
                if ts>=1:
                    timestamp.append(c.time['title'])
                else:
                    break
                ts-=1
            con = soup.findAll("button",{"class":"btn btn-outline btn-sm helpfulness-button no-margin-l"})
            for c in con:
                if h>=1:
                    dummy = c.text
                    dummy = dummy.split(' ')[-1]
                    helpful.append(int(re.search(r'\d+',str(dummy)).group()))
                else:
                    break
                h-=1
            con = soup.findAll("button",{"class":"btn-default-link link neg-feedback"})
            for c in con:
                if uh>=1:
                    dummy = c.text
                    dummy = dummy.split(' ')[-1]
                    unhelpful.append(int(re.search(r'\d+',str(dummy)).group()))
                else:
                    break
                uh-=1
        
        print('\nGoing over next product....')
        product_review = pd.DataFrame(list(zip(skuid, timestamp, rid,reviews,helpful,unhelpful)),
                                 columns =['SKUid','Datetime','RID','Review','Helpful','Unhelpful'])
        print(product_review.shape)  #validation step to make sure we scraped exactly same no of reviews
        print(product_review.head()) #see sample of product reviews added!
        return product_review


    
    
    
    
    
    
def main():
    url = 'https://www.bestbuy.com/site/tvs/65-inch-tvs/pcmcat1514910447059.c?id=pcmcat1514910447059'
    for line in open('log.txt', encoding='"ISO-8859-1"'):
        dates = line
    dates = datetime.strptime(dates, '%Y/%m/%d %H:%M %p')
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
    html = requests.get(url, headers = header, timeout=5 )                 #timeouts argument can be avoided!
        
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
    productlinks = getProductLinks(soup,total_pages,url,header)            
    del(soup)

    titles = []
    skuid = []
    modelno = []
    reviewscount = []
    
    
    product_review = pd.DataFrame(columns=['SKUid','Datetime','RID','Review','Helpful','Unhelpful'])
    i=1
    for product in productlinks:
                                                      
        product_url = 'https://www.bestbuy.com/'+str(product)
        html = requests.get(product_url, headers = header)
        soup = BeautifulSoup(html.content, 'html.parser')
        titles.append(getTitles(soup))
        skuid.append(getSKUID(soup))
        modelno.append(getModelNo(soup))
        reviewscount.append(getTotalReviewsCount(soup))
        if reviewscount[i-1]==0:
            print('No Reviews written for this product yet!')
        else:
            
            page_url = 'https://www.bestbuy.com/site/reviews/'+product.split('/')[2]+'/'    
            print('\n\n\n################# Scraping and appending reviews  ################### ')
            dt = []
            reviewcount=0
            page_url = page_url+str(skuid[i-1].strip())+'?variant=A&sort=MOST_RECENT'
            print(page_url)
            html = requests.get(page_url, headers = header)                 
            soup = BeautifulSoup(html.content, 'html.parser')
            con = soup.findAll("div", {"class":"reviews-pagination col-xs-4 col-lg-3"})
            for c in con:
                init = c.text
                tot_reviews = init.split(" ")[5]
                tot_reviews = re.sub(r',','',str(tot_reviews))
                tot_reviews = int(tot_reviews)
                if tot_reviews == 1:
                    r_icount = 1
                else:
                    r_icount = re.findall(r'-\d+',c.text)
                    r_icount = re.findall(r'\d+',str(r_icount))
                    r_icount = int(*r_icount)
                print('\nNo. of reviews in product - '+str(tot_reviews))
    
            #calculate total no of pages
            if tot_reviews<=r_icount:
                r_tot_pages = 1
            else:
                if tot_reviews%r_icount == 0:
                    r_tot_pages = tot_reviews//r_icount
                else:
                    r_tot_pages = (tot_reviews//r_icount)+1
            
            #calculate new reviews to be added count!
            if r_tot_pages>1:
                for n in range(r_tot_pages):
                    if n==0:
                        con = soup.findAll("div",{"class":"review-context"})
                        for c in con:
                            dt.append(c.time['title'])
                    else:
                        page_url_review = page_url+'&page='+str(n+1)
                        html = requests.get(page_url_review, headers = header)
                        #create new soup object for new url and scrape
                        soup1 = BeautifulSoup(html.content, 'html.parser')
                        con = soup1.findAll("div",{"class":"review-context"})
                        for c in con:
                            dt.append(c.time['title'])
                    
                    n+=1
                #transform string to datetime datatype    
                dt = [datetime.strptime(d,'%b %d, %Y %H:%M %p') for d in dt]   
                for d in dt:
                    if d>dates:
                        reviewcount+=1
                if reviewcount == 0:
                    print('No new reviews found!')
                else:
                    print('New reviews to be added are ',reviewcount)
                    #calculate pages to scrape for new reviews
                    if reviewcount<=r_icount:
                        r_tot_pages = 1
                        productreview = getReviews(page_url,i,modelno[i-1],skuid[i-1],reviewcount,r_tot_pages,tot_reviews)
                    else:
                        if reviewcount%r_icount == 0:
                            r_tot_pages = reviewcount//r_icount
                            productreview = getReviews(page_url,i,modelno[i-1],skuid[i-1],reviewcount,r_tot_pages,tot_reviews)
                        else:
                            r_tot_pages = (reviewcount//r_icount)+1
                            productreview = getReviews(page_url,i,modelno[i-1],skuid[i-1],reviewcount,r_tot_pages,tot_reviews)
            else:
                con = soup.findAll("div",{"class":"review-context"})
                for c in con:
                    dt.append(c.time['title'])
                dt = [datetime.strptime(d,'%b %d, %Y %H:%M %p') for d in dt]
                for d in dt:
                    if d>=dates:
                        reviewcount+=1
                        
                if reviewcount == 0:
                    print('No new reviews')
                else:
                    print('New reviews to be added are ',reviewcount)
                    r_tot_pages = 1
                    productreview = getReviews(page_url,i,modelno[i-1],skuid[i-1],reviewcount,r_tot_pages,tot_reviews)
        i+=1
        product_review = product_review.append(productreview,ignore_index=True)
    
    #data manipulations and sorting to append in our xlsx file
    product_review['Datetime'] = pd.to_datetime(product_review['Datetime'])
    product_review['Date'] = pd.to_datetime(product_review['Datetime']).dt.date
    product_review['Time'] = pd.to_datetime(product_review['Datetime']).dt.time
    product_review = product_review.sort_values(by=['Datetime'])
    product_review = product_review.drop(['Datetime'],axis=1)
    product_review = product_review.reset_index(drop=True)
    product_review = product_review[['SKUid','Date','Time','Review','Helpful','Unhelpful','RID']]
        
    #write dataframe into reviews file!
    writer = pd.ExcelWriter('reviews.xlsx', engine='openpyxl')
    # try to open an existing workbook
    writer.book = load_workbook('reviews.xlsx')
    # copy existing sheets
    writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
    # read existing file
    reader = pd.read_excel(r'reviews.xlsx')
    # write out the new sheet
    product_review.to_excel(writer,header=False,index=False, startrow=len(reader)+1)
    writer.close()
    
    #store current datetime to pick from while doing next update!
    dates = datetime.now()
    dates = datetime.strftime(dates, '%Y/%m/%d %I:%M %p')
    with open('log.txt','w') as f:
        f.write(dates)
    
    
    
    
