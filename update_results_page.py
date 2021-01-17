'''
NAME:           update_results_page.py
AUTHOR:         AquaDragon
DATE:           17 Jan 2021
DESCRIPTION:    Script for cleaning up player result pages on Pokemon
                Liquipedia.
'''
import re

import pywikibot
import pywikibot.pagegenerators

# Define the wiki site
lpwiki = pywikibot.Site(code='pokemon', fam='liquipedia')


# List all the pages to be edited
def catpage(var=None):
    if var is None:
        return pywikibot.pagegenerators.CategorizedPageGenerator(
            pywikibot.Category(lpwiki, 'Category:Player Results pages'),
            recurse=False, namespaces=[0], start='')  # total=10)
    else:
        return [pywikibot.Page(lpwiki, "test")]


# Edit individual pages
for page in catpage(None):
    edits = []
    text = page.text

    # Remove excessive newlines
    text, sbNL1 = re.subn('\n\n\s', '\n', text)
    text, sbNL2 = re.subn('\n\n\n', '\n\n', text)
    if sbNL1 + sbNL2 > 0:
        edits.append('Removed excessive newline skips')

    # Remove template indentation
    text, sbID1 = re.subn('\n\s\|', r'\n|', text)
    text, sbID2 = re.subn('\n\s\}\}', r'\n}}', text)
    text, sbID3 = re.subn('\n\s\{\{', r'\n{{', text)
    if sbID1 + sbID2 + sbID3 > 0:
        edits.append('Removed template indentation')

    # Remove end-of-line whitespace
    text, sbWS = re.subn('\s\n', '\n', text)
    if sbWS > 0:
        edits.append('Removed end-of-line whitespaces')

    # Look at list of templates
    templates = pywikibot.textlib.extract_templates_and_params(page.text)
    template_list = [item[0] for item in templates]

    # Replace {{Tabs static}} with {{PlayerTabsHeader}}
    if 'Tabs static' in template_list:
        id_tabs = [i for i, x in enumerate(template_list)
                   if x == 'Tabs static'][0]

        # Determine if player is broadcaster
        pagename = page.title().split('/')[0]
        page_bc = pywikibot.Page(lpwiki, "{0}/Broadcasts".format(pagename))

        if page_bc.exists():
            text = re.sub('\{\{Tabs static((.*)+\n){6,8}\}\}',
                          r'{{PlayerTabsHeader|broadcaster=yes}}', text)
            edits.append('Switched tabs to "PlayerTabsHeader" Template')
        else:
            text = re.sub('\{\{Tabs static((.*)+\n){5,7}\}\}',
                          r'{{PlayerTabsHeader}}', text)
            edits.append('Switched tabs to "PlayerTabsHeader" template')

    # Move DISPLAYTITLE to the top of the page
    try:
        displaytitle = re.search('\{\{DISPLAYTITLE:((.*)+)\}\}', text)
        test = displaytitle[1]
    except TypeError:
        pass
    else:
        temp, sbDIS = re.subn('\{\{DISPLAYTITLE:((.*)+)\}\}\n', '', text)
        temp = displaytitle[0] + '\n' + temp
        if temp != text:
            text = temp
            edits.append('Moved DISPLAYTITLE to top')

    # Remove __NOTOC__
    if re.search('__NOTOC__', text) is not None:
        text, sbTOC = re.subn('(\n*)__NOTOC__(\n*)', '\n\n', text)
        if sbTOC > 0:
            edits.append('Removed __NOTOC__')

    # Add newline between templates and section header
    text, sbNEW = re.subn('([\}_])(\n==Detailed)', '\g<1>\n\g<2>', text)
    if sbNEW > 0:
        edits.append('Added newline before section header')

    # Check if any changes to be made to the page
    if text != page.text:
        # Prepare changes to page
        page.text = text
        print(page.text)

        # Generate edit summary
        edit_summary = ', '.join(edits)
        print("\n!! Edit summary:", edit_summary)

        # Save page with edit summary
        page.save(edit_summary)
    else:
        print('No changes to {0}, page skipped'.format(page.title()))
