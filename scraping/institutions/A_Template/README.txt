This is a quick README for the data required in the institution.json file for a given institution

{
    "institution": "NAME",
    "listURLs": {"2023": "URL OF MODULE OVERVIEW PAGE FOR THE ACADEMIC YEAR 2023-24"},
    "XPath": {
        "module_id": "XPATH TO THE MODULE CODE ON A GIVEN MODULE PAGE",
        "moduleURL": "XPATH TO THE MODULE URLS ON THE MODULE OVERVIEW PAGE. THIS PAGE SHOULD CONSIST OF MULTIPLE LINKS AND MAYBE MULTIPLE TABLES OF LINKS, SO THE XPATH MAY BE NON-TRIVIAL.
                        THE EASIEST WAY IS TO COMPARE TWO MODULE CODES TO WORK OUT WHICH ELEMENT SHOULD BE REPLACED, E.G. tr[1] WITH tr[*]
                        IF MODULE CODES EXIST IN MULTIPLE TABLES, E.G. EDINBURGH, THEN COMPARE TWO XPATHS FROM DIFFERENT TABLES TO WORK OUT WHICH TABLE ELEMENT TO REPLACE WITH TABLE[*]",
        "title": "XPATH TO THE MODULE TITLE. THIS MAY END UP THE SAME AS module_id IN MANY CASES AND WE WILL SORT THIS WITH REGEX AFTERWARDS",
        "summary": "XPATH TO MODULE SUMMARY",
        "content": "XPATH TO MODULE CONTENT",
        "ilo": "XPATH TO LEARNING OUTCOMES",
        "level": "XPATH TO LEVEL",
        "credits": "XPATH TO CREDITS"
    }
}

values listURLs can either be a single string for each key (year), or a list of strings 

For example:

{
    "institution": "Edinburgh",
    "listURLs": {"2023":"http://www.drps.ed.ac.uk/23-24/dpt/cx_sb_infr.htm"},
    "XPath": {
        "module_id": "//*[@id='sitspagetitle']",                                        
        "moduleURL": "/html/body/table[2]/tbody/tr/td[1]/table[*]/tbody/tr[*]/td[3]/a",   <- Notice here the tr[*] is to grab all of the different URLs in a table. The table[*] is to grab all of the tables on the module overview page.
        "title": "/html[1]/body/table[2]/tbody/tr/td[1]/h1",
        "summary": "/html/body/table[2]/tbody/tr/td[1]/table[1]/tbody/tr[5]/td[2]",
        "content": "/html/body/table[2]/tbody/tr/td[1]/table[1]/tbody/tr[6]/td[2]",
        "ilo": "",
        "level": "/html/body/table[2]/tbody/tr/td[1]/table[1]/tbody/tr[2]/td[2]",
        "credits": "/html/body/table[2]/tbody/tr/td[1]/table[1]/tbody/tr[3]/td[2]"
    }
}