'''
NAME:           update_league_cup.py
AUTHOR:         AquaDragon
DATE:           22 Jan 2021
DESCRIPTION:    Script for cleaning up League Cup pages on Pokémon Liquipedia.
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
            pywikibot.Category(lpwiki, 'Category:Weekly Tournaments'),
            recurse=False, namespaces=[0], start='')  # , total=10)
    else:
        return [pywikibot.Page(lpwiki, "test")]


# Edit individual pages
for page in catpage(None):
    if page.title().partition('/')[0] == 'Rose Tower':
        break

    edits = []
    text = page.text

    # Remove end-of-line whitespace
    temp = re.sub('( *)\n', '\n', text)
    if text != temp:
        text = temp
        edits.append('Removed end-of-line whitespaces')

    # Look at list of templates
    templates = pywikibot.textlib.extract_templates_and_params(page.text)
    template_list = [item[0] for item in templates]

    # Update Infobox league
    if 'Infobox league' in template_list:
        tempID = [i for i, x in enumerate(template_list)
                  if x == 'Infobox league'][0]

        name = re.search('\|name=(.*)\n', text)[1]
        country = re.search('\|country=(.*)\n', text)[1]

        if country in ['United States', 'Canada']:
            citystate = re.search('League Cup - (.*) [0-9]{2}-[0-9]{2}'
                                  '-[0-9]{4}', name)
            if citystate is not None:
                current_city = re.search('\|city=(.*)\n', text)
                if re.search(current_city[1], citystate[1]) is not None:
                    text = re.sub('\|city=(.*)\n', '|city={0}\n'.
                                  format(citystate[1]), text)
                    edits.append('Updated city with state')

        # Remove shortname if equal to name
        if name == re.search('\|shortname=(.*)\n', text)[1]:
            text = re.sub('\|shortname=(.*)\n', '', text)
            edits.append('Removed shortname')

        # Remove tickername if equal to name
        if name == re.search('\|tickername=(.*)\n', text)[1]:
            text = re.sub('\|tickername=(.*)\n', '', text)
            edits.append('Removed tickername')

        # Update game played
        text = re.sub('\|game=(.*)\n', '|game=TCG\n', text)
        edits.append('Set game=TCG')

        # Add circuit name
        text = re.sub('(\|format=.*\n)(\|.*)', '\g<1>|series='
                      'Pokémon League Cup\n\g<2>', text)
        edits.append('Added series name')

        # Update Liquipedia tier
        text = re.sub('\|liquipediatier=(.*)Weekly(.*)\n',
                      '|liquipediatier=3\n', text)
        edits.append('Changed to Tier 3')

    # Update sections
    # section Tournament Details
    text = re.sub('\n==Format==\n', '\n==Tournament Details==\n'
                  '===Format===\n', text)
    edits.append("Sectioned 'Tournament Details'")

    # section Results
    temp = re.sub('===Swiss Results===', '===Swiss Rounds Standings===', text)

    if re.search('==Results==', text) is None:
        temp = re.sub('===Masters Top 8===', '==Results==\n===Single '
                      'Elimination Finals Bracket===', temp)

    temp = re.sub('===?Results?===?\n\{\{Swiss', '==Results==\n===Swiss '
                  'Rounds Standings===\n{{Swiss', temp)

    if temp != text:
        text = temp
        edits.append('Updated Results section headers')

    # If there is no description, add a description
    def description(loc_city, loc_full, date):
        return "The '''{0} League Cup''' was a trading card game tournament "\
               'held at {1} on {2}. The event was part of the Pokémon '\
               'Championship Series where players earn Championship '\
               'Points (CP) in order to qualify for the {{{{series|worlds|'\
               'Pokémon World Championships}}}}.'.format(loc_city, loc_full,
                                                          date)

    title, loc, dd = page.title().split('/')
    dd = date.fromisoformat(re.search('\|date=(.*)\n', text)[1])
    country = re.search('\|country=(.*)\n', text)[1]
    city = re.search('\|city=(.*)\n', text)[1]

    if country in ['United States', 'Canada']:
        full_loc = '{0} of the {1}'.format(city, country)
    else:
        full_loc = '{0}, {1}'.format(city, country)
    desc = description(loc, full_loc, dd.strftime("%#d %B %Y"))
    text = re.sub('(\}*\n*)(==Tournament Details==)', '\g<1>{0}\n\n\g<2>'.
                  format(desc), text)
    edits.append('Added description')

    # Update Prize Pool entries
    temp = re.sub('\|localcurrency=points', '|points=CP', text)
    temp = re.sub('\|localprize=([0-9]{1,3})[^0-9^\|^\n]*([\|\n])',
                  '|points=\g<1>\g<2>', temp)
    temp = re.sub(' *([\|}}])', '\g<1>', temp)
    if temp != text:
        text = temp
        edits.append('Updated prize pool templates')

    # Update Swiss table/row
    temp = re.sub('Swiss table/start\|rounds=0', 'Swiss table/start', text)
    temp = re.sub('\|place=(.*)\|flag=(.*)\|(.*)\|win_m=(.*)\|lose_m=(.*)\|'
                  'tie_m=(.*)\|opw%=([^%]*)%?\|oopw%=([^%]*)%?\}\}',
                  '|\g<1>| |\g<2>|\g<3>|\g<4>|\g<5>|\g<6>|\g<7>|\g<8>}}', temp)
    if temp != text:
        text = temp
        edits.append('Updated swiss standings table')

    # Add reference section
    if re.search('=References?=', text) is None:
        text += '\n\n==References==\n{{Reflist}}'
        edits.append('Appended reference section')

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
