#!/usr/bin/env python
# coding: utf-8

# Following https://realpython.com/beautiful-soup-web-scraper-python/
# and https://www.scrapingbee.com/blog/selenium-python/
# 
# 
# install webdriver for Chrome from https://developer.chrome.com/blog/chrome-for-testing/
# 
# in your python environment install selenium https://selenium-python.readthedocs.io/installation.html
# 
# to identify xpath location of relevant content can use https://selectorshub.com/selectorshub/

import json
import pandas as pd

import os

from selenium import webdriver
from selenium.webdriver.common.by import By

from pathlib import Path

import pprint

import sys

def heading(field):
    return "<h2>" + field + "</h2>"
    
def scrape(institution_name):
    institution_json = "institution.json"

    print("Scraping " + institution_name)

    pp = pprint.PrettyPrinter(indent=4)

    driver1 = webdriver.Chrome()
    driver2 = webdriver.Chrome()
    key_fields = ['institution', 'year']
    overview_fields = ['module_id', 'title', 'summary', 'content', 'ilo', 'level', 'credits']
    all_fields = key_fields + overview_fields

    try:
        path = institution_name

        with open(os.path.join(path, institution_json)) as institution_file:
            institution_config = json.load(institution_file)
            pp.pprint(institution_config)
        electives_df = pd.DataFrame(columns=all_fields, dtype="string")

        listURLs = institution_config['listURLs']     
        xpaths = institution_config['XPath']

# dictionary structure: year > module code > feature
        results = {}


        for year in listURLs:
            results[year] = {}
            listURL = listURLs[year]
#            print ("year ", year, "lURL", listURL)
            driver1.get(listURL)
            moduleURLPath = institution_config['XPath']['moduleURL']
            moduleURLs = driver1.find_elements(By.XPATH, moduleURLPath)
            for mURL in moduleURLs:
                # TODO save whole index page
                moduleURL = mURL.get_attribute('href')
                print("moduleURL", moduleURL)
                driver2.get(moduleURL)
                overview_dictionary = {}

                for overview_field in overview_fields:
                    overview_dictionary[overview_field] = ""
                    try:
                        overview_elts = driver2.find_elements(By.XPATH, xpaths[overview_field])
                    except Exception:
    #                    print("Could not find field " + overview_field)
                        continue
                    for elt in overview_elts:
    #                    print ("found elt for " + overview_field)
                        innerHTML = elt.get_attribute('innerHTML')
                        overview_dictionary[overview_field] += innerHTML
                results[year][overview_dictionary['module_id']] = overview_dictionary
        with open(Path(os.path.join(institution_name,"scrape_results.json")), "w") as outfile: 
            json.dump(results, outfile)

    except OSError as err:
        print("OS error:", err)
        driver1.quit()
        driver2.quit()
# scrape to get list of modules
        
# scrape all the modules

'''


#            full_page=driver.find_elements(By.XPATH, '//').get_attribute('innerHTML')
#            full_file = open("Page" + elective, "w")
#            full_file.write(full_page)
#            full_file.close()
            overview = heading(institution_name + " " + elective)
            overview_dictionary = {}
            for overview_field in overview_fields:
                overview_dictionary[overview_field] = ""
                try:
                    overview_elts = driver.find_elements(By.XPATH, xpaths[overview_field])
                except Exception:
#                    print("Could not find field " + overview_field)
                    continue
                overview += heading(overview_field)
                for elt in overview_elts:
#                    print ("found elt for " + overview_field)
                    innerHTML = elt.get_attribute('innerHTML')
                    overview += innerHTML
                    overview_dictionary[overview_field] += innerHTML
            new_row = {"institution": institution_config['institution'],
                    "elective": elective,
                    "overview": overview} | overview_dictionary
            electives_df = electives_df.append(new_row, ignore_index=True)
        electives_df = electives_df[electives_df['elective'].str.len() >0]
        electives_missing_df = electives_df[electives_df['title'].str.len() ==0]['elective']

# from https://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist        
        Path(os.path.join(path,'electives_missing.csv')).unlink(missing_ok=True)

        if(len(electives_missing_df.index)) >0:
            electives_missing_df.to_csv(os.path.join(path,'electives_missing.csv'), index=False)

        electives_df.to_csv(os.path.join(path,'electives_scraped.csv'), index=False)
        driver.quit()

'''

def main():
    try:
        arg = sys.argv[1]
        institution_name = arg
        scrape(institution_name)
    except IndexError:
        print("No institution defined on command line")
        return

if __name__ == "__main__":
    main()
