'''
NAME:           upload_sprites.py
AUTHOR:         AquaDragon
DATE:           19 Jun 2021
DESCRIPTION:    Script for uploading Pokémon sprites to Liquipedia commons.
'''
import pywikibot
import pywikibot.pagegenerators

import subprocess

# Define the wiki site
lpwiki = pywikibot.Site(code='commons', fam='liquipedia')

ii = 0

# List of sprites to upload
f = open('./scripts/userscripts/uploadlist.txt', 'r')

for mon in f.read().splitlines():
    # if ii == 50:
    #     break

    # Sprite source filename
    prefix = "https://raw.githubusercontent.com/msikma/pokesprite/master/"\
             "pokemon-gen8/regular/"
    sourcefname = prefix + mon + '.png'

    # Naming scheme on Liquipedia
    fname = 'pkmn-' + mon + '.png'

    descfile = "== Summary ==\n{{{{FileInfo\n|featured=\n|featured2=\n"\
               "|description=A Pokémon sprite of {0}\n"\
               "|license=fairuse\n|game=pokemon\n|event=\n|date=\n"\
               "|author=Pokémon\n"\
               "|copyright=Nintendo / Creatures Inc. / GAME FREAK Inc.\n"\
               "|note=\n"\
               "|source=Sprites are sourced from the PokéSprite project, a"\
               " database for Pokémon sprites."\
               " (https://msikma.github.io/pokesprite/)\n"\
               "}}}}\n\n[[Category:Pokémon sprites]]".format(
                    mon.replace('-', ' ').title())

    # Check if page already exists on wiki so we don't have to wait
    page = pywikibot.Page(lpwiki, 'File:{0}'.format(fname))

    if not page.exists():
        subprocess.call(['py', 'pwb.py', './scripts/upload.py',
                         '-filename:{0}'.format(fname), sourcefname, descfile,
                         '-abortonwarn', '-ignorewarn', '-always'])

    ii += 1

f.close()
