This is a quick README for the data required in the institution.json file for a given institution

{
    "institution": "NAME",
    "index": {"2023": [{"url": "URL OF MODULE OVERVIEW PAGE FOR THE ACADEMIC YEAR 2023-24"}]},
    "module": {
        "moduleContainers": {"XPath": "XPATH TO THE MODULES ON THE MODULE OVERVIEW PAGE. THIS PAGE SHOULD CONSIST OF MULTIPLE LINKS AND MAYBE MULTIPLE TABLES OF LINKS, SO THE XPATH MAY BE NON-TRIVIAL.
                        THE EASIEST WAY IS TO COMPARE TWO MODULE CODES TO WORK OUT WHICH ELEMENT SHOULD BE REPLACED, E.G. tr[1] WITH tr[*]
                        IF MODULE CODES EXIST IN MULTIPLE TABLES, E.G. EDINBURGH, THEN COMPARE TWO XPATHS FROM DIFFERENT TABLES TO WORK OUT WHICH TABLE ELEMENT TO REPLACE WITH TABLE[*]",
                            "exclude": ["regexp on module link to exclude"],
                            "include": ["regexp on module link to include"],
                            "moduleLink": {"XPath": "XPATH to module link within the container, relative to container. If not specified then then moduleContainers.XPath is used by itself. Useful for when there is a table including module links and other information we need e.g. number of credits"},
                            "credits": {"XPath": "XPATH to credits within the index container, relative to container. Use only if not defined in the module page. Same for all fields e.g. level"}
                },
        "module_id": {"XPath": "XPATH TO THE MODULE CODE ON A GIVEN MODULE PAGE"},
        "title": {"XPath": "XPATH TO THE MODULE TITLE. THIS MAY END UP THE SAME AS module_id IN MANY CASES AND WE WILL SORT THIS WITH REGEX AFTERWARDS"},
        "summary": {"XPath": "XPATH TO MODULE SUMMARY"},
        "content": {"XPath": "XPATH TO MODULE CONTENT"},
        "ilo": {"XPath": "XPATH TO LEARNING OUTCOMES"},
        "level": {"XPath": "XPATH TO LEVEL"},
        "credits": {"XPath": "XPATH TO CREDITS"}
    }
}

If all of the data is held inside the index page then include '"no_clicking_required": true' in the spec (see Northampton)

Actions to navigate from the index page to the list of modules can be specified in the "index" items e.g.

"index": {"2023": {"url": "URL of starting point":
                            [{"XPath": "XPath selector of select element",
                               "action": "select",
                               "data": "Text of label to select"},
                            {"XPath": "XPath selector of button or anchor element",
                            "action": "click"}]}}

If "when": "first" is included as an action property then it is only done the first time the page is loaded: helpful for accepting cookies

Clicking on buttons can be specified via "ID" rather than "XPath". This is often helpful for accepting cookies.

