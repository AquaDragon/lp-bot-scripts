'''
NAME:           move_lc_pages.py
AUTHOR:         AquaDragon
DATE:           27 Mar 2021
DESCRIPTION:    Script for moving League Cup pages on Pokémon Liquipedia.
'''
from datetime import date, datetime
import re

import pywikibot
import pywikibot.pagegenerators

# Define the wiki site
lpwiki = pywikibot.Site(code='pokemon', fam='liquipedia')


# List all the pages to be edited
def catpage(var=None):
    if var is None:
        return pywikibot.pagegenerators.CategorizedPageGenerator(
            pywikibot.Category(lpwiki, 'Category:Tier_3_Tournaments'),
            recurse=False, namespaces=[0], start='Pokemon League Cup/')
    else:
        return [pywikibot.Page(lpwiki, "test")]


# Edit individual pages
for page in catpage(None):
    # use dir() to load properties
    title_old = page.title()

    # Dissect the page title, then reformat
    if page.title().partition('/')[0] == 'Pokemon League Cup':
        lc, loc, date = page.title().rsplit('/')
        dd, mm, yy = date.split('-')

        if len(yy) == 2:
            yy = '20{0}'.format(yy)

        title_new = 'Pokemon Championships/League Cup/{0}/{1}-{2}-{3}'.\
                    format(loc, yy, mm, dd)

        print('page move: {0} >>>> {1}'.format(title_old, title_new))

        page.move(title_new, reason='consistent formatting of tournament URL',
                  noredirect=True)
