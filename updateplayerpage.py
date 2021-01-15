'''
NAME:           updateplayerpage.py
AUTHOR:         AquaDragon
DATE:           15 Jan 2021
DESCRIPTION:    Script for cleaning up player pages on Pokemon Liquipedia.
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
            pywikibot.Category(lpwiki, 'Category:Players'),
            recurse=False, start='Niko')
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

    templates = pywikibot.textlib.extract_templates_and_params(page.text)
    template_list = [item[0] for item in templates]

    # Replace {{Tabs static}} with {{PlayerTabsHeader}}
    if 'Tabs static' in template_list:
        id_tabs = [i for i, x in enumerate(template_list)
                   if x == 'Tabs static'][0]

        # Determine if player is broadcaster and has a 3rd tab.
        retabs = re.search('\|link3=(.*)', text)
        if retabs:
            # Check two conditions for tab to be replaced.
            retabs_name = re.search('\|name3=(.*)', text)[1]
            retabs_exist = pywikibot.Page(lpwiki, retabs[1]).exists()
            if retabs_name == 'Broadcasts' and retabs_exist:
                text = re.sub('\{\{Tabs static((.*)+\n){7,9}\}\}',
                              r'{{PlayerTabsHeader|broadcaster=yes}}', text)
                edits.append('Switched tabs to "PlayerTabsHeader" Template')
            else:
                text = re.sub('\{\{Tabs static((.*)+\n){7,9}\}\}',
                              r'{{PlayerTabsHeader}}', text)
                edits.append('Switched tabs to "PlayerTabsHeader" template')
        else:
            text = re.sub('\{\{Tabs static((.*)+\n){5,7}\}\}',
                          r'{{PlayerTabsHeader}}', text)
            edits.append('Switched tabs to "PlayerTabsHeader" template')

    if 'Infobox player' in template_list:
        idINFBX = [i for i, x in enumerate(template_list)
                   if x == 'Infobox player'][0]
        params_list = templates[idINFBX][1]

        id_param = re.search('\|id=((.*)+)\n', text)

        # Remove DISPLAYTITLE if entry is the same as id in {{Infobox player}}
        try:
            displaytitle = re.search('\{\{DISPLAYTITLE:((.*)+)\}\}', text)
            test = displaytitle[1]
        except TypeError:
            pass
        else:
            if displaytitle[1] == id_param[1]:
                text = re.sub('\{\{DISPLAYTITLE:((.*)+)\}\}\n', '', text)
                edits.append('Removed DISPLAYTITLE')

        # Identify TCG player. Check if ID is two fragments (usually a name),
        # then check if a substitution can be done.
        idfrag = id_param[0].split(' ')
        if len(idfrag) > 1:
            text, tcgsubs = re.subn('(\[\[(.*?)Category(.*?)\]\]) player',
                                    '\g<1> Pokémon TCG player', text)
            if tcgsubs > 0:
                edits.append('Identified TCG player')

        # Bold Player ID/alias. First check if there exist a bolded
        # name/alias, if not search the lead and bold it.
        id_clean = re.sub(r'\s+$', '', id_param[1])    # Clean trailing spaces
        if not re.compile("'''{0}'''".format(id_clean)).search(text):
            text, boldsubs = re.subn('(\n[^\|](.*)){0}((.*) is a)'.
                                     format(id_clean), "\g<1>'''{0}'''\g<3>".
                                     format(id_clean), text)
            if boldsubs > 0:
                edits.append('Bold player name/alias')

        # Remove URL prefixes in {{Infobox player}}.
        # Goes through social media list and see if entries can be segmented.
        # If it does, it most likely has a URL prefix.
        social_prefix = {
            'askfm':     'ask.fm',
            'azubu':     'www.azubu.tv',
            'douyu':     'www.douyu.com',
            'facebook':  'facebook.com',
            'gplus':     'plus.google.com',
            'instagram': 'www.instagram.com',
            'reddit':    'www.reddit.com/user',
            'steam':     'steamcommunity.com/profiles',
            'tencent':   't.qq.com',
            'twitch':    'www.twitch.tv',
            'twitter':   'twitter.com',
            'vk':        'vk.com',
            'weibo':     'weibo.com',
            'youtube':   'www.youtube.com',
            }

        social_list = ['askfm', 'azubu', 'douyu', 'facebook', 'gplus',
                       'instagram', 'reddit', 'steam', 'tencent', 'twitch',
                       'twitter', 'vk', 'weibo', 'youtube']

        flagURL = 0
        for ii in social_list:
            try:
                test = params_list[ii]
            except KeyError:
                pass
            else:
                res = re.compile('(\|{0}=)((.*)+)'.format(ii)).search(text)
                frag = res[2].split('/')

                if len(frag) > 1:
                    # Special case for youtube where "channel/someID" is
                    # required to direct to the user page
                    if ii == 'youtube' and frag[0] in ['channel']:
                        pass
                    else:
                        text = re.sub('(\|{0}=)((.*)+)'.format(ii),
                                      res[1] + frag[-1], text)
                        if flagURL == 0:
                            edits.append('Removed social media URL prefix')
                            flagURL += 1

    # Add reference section if missing
    flagref0 = pywikibot.textlib.does_text_contain_section(
                    page.text, "References"
               )
    flagref1 = pywikibot.textlib.does_text_contain_section(
                    page.text, "Reference"
               )
    if not flagref0:
        # If there is completely no reference section
        if not flagref1:
            text += "\n\n==References== \n{{Reflist}}"
            edits.append('Added reference section')
        # If there is section labelled 'Reference' without "s"
        else:
            text = re.sub('==Reference==', '==References==', text)
            edits.append('Update References')

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
