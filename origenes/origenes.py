#!/bin/python
# -*- coding: utf8 -*-
# origenes.py - Consulta en el Nuevo Tesoro Lexicográfico el año y diccionario
#               en el que se recogió una palabra por primera vez.
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

import sys
import urllib2
import cookielib
import re


class Ntlle(object):

    def __init__(self):
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        self.opener.open('http://buscon.rae.es/ntlle/SrvltGUILoginNtlle')
        form = self.opener.open(
            "http://buscon.rae.es/ntlle/jsp/CritLemaGr.jsp"
        ).read()

        m = re.search(
            '<INPUT TYPE="HIDDEN" NAME="sec" VALUE="(?P<sec>.*?)"',
            form
        )
        if not m:
            sys.exit('Error de parseo.')

        self.sec = m.groupdict()['sec']

    def origen(self, palabra):

        sq = urllib2.quote(palabra.encode('latin1'))
        self.opener.open(
            "http://buscon.rae.es/ntlle/SrvltGUIBusLema?LEMA=%s&ORDEN=1&"
            "PRIMERA=1&PERFIL=-1&DICCIONARIO=-1&sec=%s" % (sq, self.sec)
        )
        res = self.opener.open(
            "http://buscon.rae.es/ntlle/jsp/NtlLemaRes.jsp"
        ).read()

        m = re.search(
            '<TD align="left"> <font size=-2>(?P<dicc>.*?)</font> </TD>',
            res
        )
        if not m:
            raise ValueError('No se ha encontrado la palabra: %s.' % palabra)

        return m.groupdict()['dicc'].strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Uso: %s palabra1 [palabra2...]' % sys.argv[0])

    ntlle = Ntlle()
    origenes = []
    for palabra in sys.argv[1:]:
        try:
            print "%s: %s" % (
                palabra,
                ntlle.origen(palabra.decode('utf8'))
            )
        except ValueError, e:
            print e.message
