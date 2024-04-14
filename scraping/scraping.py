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
from selenium.common import ElementClickInterceptedException


from pathlib import Path

import pprint

import sys

import re

done_actions = []

def heading(field):
    return "<h2>" + field + "</h2>"

# advice from https://stackoverflow.com/questions/73525437/elementclickinterceptedexception-element-click-intercepted-element-is-not-clic
# and https://www.lambdatest.com/blog/element-is-not-clickable-at-point-exception/
# and https://www.scrapingbee.com/webscraping-questions/selenium/how-to-scroll-to-element-selenium/
def click_element(driver, element_by):
    wait = WebDriverWait(driver, 1)
    elt = wait.until(EC.element_to_be_clickable(element_by))
    driver.execute_script("arguments[0].scrollIntoView();", elt)
    try:
        elt.click()
    except ElementClickInterceptedException:
        try:
            elt.click()          
        except Exception:
            driver.execute_script("arguments[0].click();", elt)

# using the given web driver load the page specified, possibly with actions to follow
def load_content(driver, url_spec):
    # print ("loadContent from URLspec")
    # print (URLspec)
    if(type(url_spec) is str):
        load_url = url_spec
    else:
        load_url = url_spec['url']
    driver.get(load_url)
    if ('actions' in url_spec.keys()) and (type(actions := url_spec['actions']) is list):
        for action_spec in actions:
            select_by = None
            # print ("About to do action", json.dumps(actionSpec))
            # input("Hit enter")
            if 'when' in action_spec.keys():
                if action_spec['when'] == "first":
                    action_spec_str = json.dumps(action_spec)
                    if action_spec_str in done_actions:
                        continue
                    else:
                        done_actions.append(action_spec_str)

            if 'XPath' in action_spec.keys():
                select_by = (By.XPATH, action_spec['XPath'])


            if 'Link' in action_spec.keys():
                select_by = (By.PARTIAL_LINK_TEXT, action_spec['Link'])
            
            if not select_by:
                raise ValueError("No select_by for " + json.dumps(action_spec))
            
            action = action_spec['action']

            if action == "click":
                click_element(driver, select_by)
            elif action == "select":
                option = action_spec['data']
                # print ("selecting element " + option)
                select = Select(driver.find_element(element_by))
                select.select_by_visible_text(option)
            

def scrape(institution_name):
    institution_json = "institution.json"

    print("Scraping " + institution_name)

    pp = pprint.PrettyPrinter(indent=4)

    driver1 = webdriver.Chrome()
    # driver1.implicitly_wait(2)
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

# results stored during initial scan of index page
# structure: year > module link > feature 
        index_results = {}

        all_module_links = set()

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

            year_indexes = index[year]
            if not type(year_indexes) is list:
                year_indexes = [year_indexes]
            for year_index in year_indexes:
                year_module_links = set()

                # print ("year ", year, "lURL", yearIndex)
                load_content(driver1, year_index)
                
                # print ("Loaded contents of index page for year ")
                container_spec = module['moduleContainers']
                if 'XPath' in container_spec.keys():
                    module_containers = driver1.find_elements(By.XPATH, container_spec['XPath'])
                elif 'CSS_class' in container_spec.keys():
                    module_containers = driver1.find_elements(By.CLASS_NAME, container_spec['CSS_class'])
                else:
                    raise ValueError("No moduleContainer specification for " + year_index)



                print("Found some URL elements ", len(module_containers))
                for module_container in module_containers:
                    # get rid of any newly opened tabs
                    while(len(driver1.window_handles) >1 ):
                        remove_handle = driver1.window_handles[-1]
                        driver1.switch_to.window(remove_handle)
                        driver1.close()
                    driver1.switch_to.window(driver1.window_handles[0])

                    mmc = module['moduleContainers']

                    # print ("moduleContainer", moduleContainer)
                    if 'moduleLink' in mmc.keys():
                        module_link_path = mmc['moduleLink']['XPath']
                        # print ("moduleLinkPath ", moduleLinkPath)
                        module_link_elt = module_container.find_element(By.XPATH, module_link_path)
                    else:
                        module_link_elt = module_container
                    module_link = html.unescape(module_link_elt.get_attribute('innerHTML').strip())
                    if (type(module_link) is str) and (len(module_link) > 0) and  (not (module_link in all_module_links)):
                        if 'exclude' in mmc.keys():
                            exclude = False
                            for exclude_re in mmc['exclude']:
                                if re.match(exclude_re, module_link):
                                    exclude = True
                                    break
                            if exclude:
                                print ("excluding " + module_link)
                                continue
                        if 'include' in mmc.keys():
                            include = False
                            for include_re in mmc['include']:
                                if re.match(include_re, module_link):
                                    include = True
                                    break
                            if not include:
                                print ("not including " + module_link)
                                continue

                        
                        # print ("adding moduleLink",  moduleLink)
                        year_module_links.add(module_link)
                        all_module_links.add(module_link)

                # print ("yearModuleLinks[ ", list(yearModuleLinks)[0:200])

                for module_link in year_module_links:
                    load_content(driver1, year_index)
                    try:
                        print ("looking for link " + module_link)
                        click_element(driver1, (By.PARTIAL_LINK_TEXT,  module_link))

                        overview_dictionary = {}

                        for overview_field in overview_fields:
                            overview_dictionary[overview_field] = ""
                            try:
                                overview_elts = driver1.find_elements(By.XPATH, module[overview_field]['XPath'])
                            except Exception:
                                # print("Could not find field " + overview_field)
                                continue
                            for elt in overview_elts:
                                # print ("found elt for " + overview_field)
                                innerHTML = elt.get_attribute('innerHTML').strip()
                                if overview_field == "module_id":
                                    innerHTML = strip_tags(innerHTML)
                                overview_dictionary[overview_field] += innerHTML
                        results[year][overview_dictionary['module_id']] = overview_dictionary
                    except Exception as e:
                        print ("Could not find link " + module_link)
                        print (year_index)
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
