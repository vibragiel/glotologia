#!/bin/python
# -*- coding: utf8 -*-
# enmiendas-drae.py
#
# Copyright (C) 2013 Gabriel Rodríguez Alberich <chewie@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from lxml import html
from urllib2 import quote
import argparse
import json
import locale
import re
import requests
import sys


_USERAGENT = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.5)' \
             ' Gecko/2008121622 Ubuntu/8.04 (hardy) Firefox/3.0.5'
headers = {'User-Agent': _USERAGENT}
challenge = [
    ('TS014dfc77_id', 3),
    ('TS014dfc77_cr',
     '1a285e2c3a9cd4734a6c9e597c92c6f5:jihl:c55Mjc2J:1073656524'),
    ('TS014dfc77_76', 0),
    ('TS014dfc77_md', 1),
    ('TS014dfc77_rf', 0),
    ('TS014dfc77_ct', 0),
    ('TS014dfc77_pd', 0)
]

BASE_URL = 'http://lema.rae.es'
URL = BASE_URL + '/enmDRAE/cgi-bin/enmDRAE.cgi?%(letter)s=%(letter)s&' \
                 'np=%(np)d&ne=%(ne)d&nep=102'


def clean_lemma(string):
    """Strip periods, superscript numbers and spare whitespaces"""
    string = re.sub(u"\.?$", "", string).strip()
    string = re.sub("[0-9]", "", string)
    string = string.strip()
    return string


def get_amended_lemmas():
    """Retrieves all amendments to the DRAE. Returns a list of dictionaries
       with the lemmas and the type of change made (amendment, addition or
       suppression)."""
    lemmas = []
    len_lemma = 0
    for letter in u"ABCDEFGHIJKLMNÑOPQRSTUVWXYZ":
        sys.stderr.write("Downloading lemmas starting with %s... " % letter)
        upar = {'letter': quote(letter.encode('utf8')),
                'np': 1,
                'ne': 1}
        while True:
            url = URL % upar
            response = requests.post(url, data=challenge, headers=headers)
            root = html.fromstring(response.content)
            emn = root.xpath("//div[@id='amend']//td[@class='am']/a")
            if not emn:
                break
            for a in emn:
                lema_url = BASE_URL + a.attrib['href'].replace("/enmDRAE/",
                                                               "/drae/")
                g = requests.post(lema_url, data=challenge, headers=headers)
                l_root = html.fromstring(g.content.decode('utf8'))
                enm_link = l_root.\
                    xpath("//a/img[contains(@alt, 'enmendado')]/..")
                # if "Artículo enmendado" button is present, download the
                # amended version
                if enm_link:
                    lema_url = "%s/drae/srv/%s" % \
                        (BASE_URL, enm_link[0].attrib['href'])
                    g = requests.post(lema_url, data=challenge,
                                      headers=headers)
                    l_root = html.fromstring(g.content.decode('utf8'))

                l_lemmas = []
                # get all lemmas in the article, in case the definitions were
                # splitted
                p_lemmas = l_root.xpath("//p[@class='p']/span[@class='f']/..")
                for p_lemma in p_lemmas:
                    lemma = {}
                    lemma['lemma'] = clean_lemma(p_lemma.text_content())
                    sys.stderr.write("\b \b" * len_lemma + lemma['lemma'])
                    len_lemma = len(lemma['lemma'])
                    # grabs the message containing the sort of change made to
                    # the article
                    change = p_lemma.\
                        xpath("../p[@class='l' and position()=1]/text()")[0]
                    if "enmendado" in change:
                        lemma['change'] = "a"
                    elif "nuevo" in change:
                        lemma['change'] = "n"
                    elif "suprimido" in change:
                        lemma['change'] = "s"
                    else:
                        lemma['change'] = "?"
                    l_lemmas.append(lemma)
                lemmas.extend(l_lemmas)

            upar['np'] += 1
            upar['ne'] += 102

        sys.stderr.write("\b \b" * len_lemma + "OK\n")
        len_lemma = 0

    return lemmas


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Enmiendas del DRAE'
    )
    parser.add_argument(
        '-w', '--wordlist',
        action='store_true',
        help='wordlist mode: print just a word list with no metadata'
    )
    parser.add_argument(
        '-n', '--hide-new',
        action='store_true',
        help='don\'t print new articles'
    )
    parser.add_argument(
        '-s', '--hide-suppressed',
        action='store_true',
        help='don\'t print suppressed articles'
    )
    parser.add_argument(
        '-a', '--hide-amended',
        action='store_true',
        help='don\'t print amended articles'
    )
    args = parser.parse_args()

    lemmas = get_amended_lemmas()

    if args.hide_new:
        lemmas = [x for x in lemmas if x['change'] != "n"]
    if args.hide_suppressed:
        lemmas = [x for x in lemmas if x['change'] != "s"]
    if args.hide_amended:
        lemmas = [x for x in lemmas if x['change'] != "a"]

    # try to sort the lemmas with the Spanish locale
    try:
        locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")
    except locale.Error:
        locale.setlocale(locale.LC_ALL, "")
    lemmas.sort(cmp=locale.strcoll, key=lambda x: x['lemma'])

    # print wordlist or json
    if args.wordlist:
        print "\n".join([x['lemma'] for x in lemmas]).encode("utf8")
    else:
        print json.dumps(lemmas, ensure_ascii=False).encode("utf8")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write("\n")
        sys.exit(0)
