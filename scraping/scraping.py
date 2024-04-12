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

import html

from strip_tags import strip_tags

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from pathlib import Path

import pprint

import sys

import re

done_actions = []

def heading(field):
    return "<h2>" + field + "</h2>"

# using the given web driver load the page specified, possibly with actions to follow
def loadContent(driver, URLspec):
    # print ("loadContent from URLspec")
    # print (URLspec)
    if(type(URLspec) is str):
        loadURL = URLspec
    else:
        loadURL = URLspec['url']
    driver.get(loadURL)
    if ('actions' in URLspec.keys()) and (type(actions := URLspec['actions']) is list):
        for actionSpec in actions:
            elt = None
            # print ("About to do action", json.dumps(actionSpec))
            # input("Hit enter")
            if 'when' in actionSpec.keys():
                if actionSpec['when'] == "first":
                    actionSpecStr = json.dumps(actionSpec)
                    if actionSpecStr in done_actions:
                        continue
                    else:
                        done_actions.append(actionSpecStr)

            if 'XPath' in actionSpec.keys():
                print ("Selecting element at xpath ", actionSpec['XPath'])
                elt = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, actionSpec['XPath'])))

            if 'Link' in actionSpec.keys():
                print ("Selection element with link ", actionSpec['Link'])
                elt = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, actionSpec['Link'])))
            
            if not elt:
                raise ValueError("No element found for " + json.dumps(actionSpec))
            
            action = actionSpec['action']

            if action == "click":
                elt.click()
            elif action == "select":
                option = actionSpec['data']
                # print ("selecting element " + option)
                select = Select(elt)
                select.select_by_visible_text(option)
            

def scrape(institution_name):
    institution_json = "institution.json"

    print("Scraping " + institution_name)

    pp = pprint.PrettyPrinter(indent=4)

    driver1 = webdriver.Chrome()
    driver1.implicitly_wait(2)
    # driver2 = webdriver.Chrome()
    key_fields = ['institution', 'year']
    overview_fields = ['module_id', 'title', 'summary', 'content', 'ilo', 'level', 'credits']
    all_fields = key_fields + overview_fields

    try:
        path = institution_name

        with open(os.path.join(path, institution_json)) as institution_file:
            institution_config = json.load(institution_file)
            pp.pprint(institution_config)
        electives_df = pd.DataFrame(columns=all_fields, dtype="string")

        index = institution_config['index']     
        module = institution_config['module']


# dictionary structure: year > module code > feature
        results = {}

        allModuleLinks = set()

        for year in index:
            results[year] = {}
# the same module may appear in different programmes, so merge them into a set

            #Create a folder for module webpages of a given year. Check if folder exists already otherwise you'll get a FileExistsError
            try:
                dir = os.path.join(path, year)
                if not os.path.exists(dir):  
                    os.mkdir(dir)  
            except OSError as error:  
                print(error)

            yearIndexes = index[year]
            if not type(yearIndexes) is list:
                yearIndexes = [yearIndexes]
            for yearIndex in yearIndexes:
                yearModuleLinks = set()

                # print ("year ", year, "lURL", yearIndex)
                loadContent(driver1, yearIndex)
                
                # print ("Loaded contents of index page for year ")
                containerSpec = module['moduleContainers']
                if 'XPath' in containerSpec.keys():
                    moduleContainers = driver1.find_elements(By.XPATH, containerSpec['XPath'])
                elif 'CSS_class' in containerSpec.keys():
                    moduleContainers = driver1.find_elements(By.CLASS_NAME, containerSpec['CSS_class'])
                else:
                    raise ValueError("No moduleContainer specification for " + yearIndex)



                print("Found some URL elements ", len(moduleContainers))
                for moduleContainer in moduleContainers:
                    mmc = module['moduleContainers']

                    # print ("moduleContainer", moduleContainer)
                    if 'moduleLink' in mmc.keys():
                        moduleLinkPath = mmc['moduleLink']['XPath']
                        # print ("moduleLinkPath ", moduleLinkPath)
                        moduleLinkElt = moduleContainer.find_element(By.XPATH, moduleLinkPath)
                    else:
                        moduleLinkElt = moduleContainer
                    moduleLink = html.unescape(moduleLinkElt.get_attribute('innerHTML').strip())
                    if (type(moduleLink) is str) and (len(moduleLink) > 0) and  (not (moduleLink in allModuleLinks)):
                        if 'exclude' in mmc.keys():
                            exclude = False
                            for exclude_re in mmc['exclude']:
                                if re.match(exclude_re, moduleLink):
                                    exclude = True
                                    break
                            if exclude:
                                print ("excluding " + moduleLink)
                                continue
                        if 'include' in mmc.keys():
                            include = False
                            for include_re in mmc['include']:
                                if re.match(include_re, moduleLink):
                                    include = True
                                    break
                            if not include:
                                print ("not including " + moduleLink)
                                continue

                        
                        # print ("adding moduleLink",  moduleLink)
                        yearModuleLinks.add(moduleLink)
                        allModuleLinks.add(moduleLink)

                # print ("yearModuleLinks[ ", list(yearModuleLinks)[0:200])

                for moduleLink in yearModuleLinks:
                    loadContent(driver1, yearIndex)
                    try:
                        # print ("looking for link " + moduleLink)
                        linkElt = WebDriverWait(driver1, 1).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT,  moduleLink)))
                        # print ("found link " + moduleLink)
                        linkElt.click()
                        overview_dictionary = {}

                        for overview_field in overview_fields:
                            overview_dictionary[overview_field] = ""
                            try:
                                overview_elts = driver1.find_elements(By.XPATH, module[overview_field]['XPath'])
                            except Exception:
            #                    print("Could not find field " + overview_field)
                                continue
                            for elt in overview_elts:
            #                    print ("found elt for " + overview_field)
                                innerHTML = elt.get_attribute('innerHTML').strip()
                                if overview_field == "module_id":
                                    innerHTML = strip_tags(innerHTML)
                                overview_dictionary[overview_field] += innerHTML
                        results[year][overview_dictionary['module_id']] = overview_dictionary
                    except Exception as e:
                        print ("Could not find link " + moduleLink)
                        print (yearIndex)
                        print (e)


                    #Save the contents of this URL as a HTML file. Use the module_id as the filename
                    #Remove any whitespace and punctuation from module_id
                    page = re.sub('\W+','',overview_dictionary['module_id']) + '.html'
                    
                    with open(os.path.join(dir,page), "w", encoding='utf-8') as modFile:
                        modFile.write(driver1.page_source)





            # print("moduleURLs", yearModuleURLs)

            # for yearIndex in yearIndexes:
            # for yearModuleLink in yearModuleLinks:
            #     print("moduleURL", moduleURL)
            #     driver2.get(moduleURL)

                #Consider the level information. Try to figure out the year in either SCQF or Degree Year form
                #numbersInLevel = re.findall(r'\d+', overview_dictionary['level'])
                #print(numbersInLevel)

                # degYear=""
                # SCQF = ""
                # CQFW = ""
                #Some institutions provide SCQF, some CQFW and others degree year. Ref: https://www.sqa.org.uk/sqa/64561.html
                #It is possible we end up with many values stored if a University provides multiple pieces of information, e.g. Edinburgh
                #Working assumption: if we see the words SCQF or CQFW we take the next number we find as their value. If we see a number with neither of these assume it is degree year.
                # tokens = overview_dictionary['level'].split()
                # i=0
                # while i<len(tokens):
                #     if tokens[i] == "SCQF":
                #         for j in range(i, len(tokens)):
                #             if (tokens[j].isnumeric()):
                #                 #This is the next number following SCQF, so assume it is the level
                #                 SCQF = tokens[j]
                #                 i=j+1
                #                 break
                #     elif tokens[i] == "CQFW":
                #         for j in range(i, len(tokens)):
                #             if (tokens[j].isnumeric()):
                #                 #This is the next number following CQFW, so assume it is the level
                #                 CQFW = tokens[j]
                #                 i=j+1
                #                 break
                #     elif tokens[i].isnumeric():
                #         #We've found a number that wasn't preceeded by either SCQF or CQFW, so assume it is the degree level
                #         degYear = tokens[i]
                #     i=i+1


                # print("Degree Year: ", degYear)
                # print("SCQF Level: ", SCQF)
                # print("CQFW Level: ", CQFW)

        with open(Path(os.path.join(institution_name,"scrape_results.json")), "w") as outfile: 
            json.dump(results, outfile, indent=2)

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
