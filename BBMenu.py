# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 20:45:31 2020

@author: shail
"""

import dailyrun
import test_review_updates


choice ='0'
while choice =='0':
    print("######################  MENU ###########################")
    print("1: Scrape Todays Product Prices and Star Ratings")
    print("2: Scrape review from last scrape date")
    print("3: Exit")

    choice = input ("Please enter your choice: ")

    if choice == "1":
        dailyrun.main()
    elif choice == "2":
        test_review_updates.main()
    elif choice == "3":
        exit()
    else:
        print("Invalid Choice!!")

