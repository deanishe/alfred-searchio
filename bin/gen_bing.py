#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-09
#

"""Generate Bing engine JSON."""

from __future__ import print_function, absolute_import

from collections import namedtuple
import json

from common import mkdata, mkvariant

# Languages from https://msdn.microsoft.com/en-us/library/dd250941.aspx
LANGS = u"""
aa
Afar
ab
Abkhazian
ae
Avestan
af
Afrikaans
ak
Akan
am
Amharic
an
Aragonese
ar
Arabic
as
Assamese
av
Avaric
ay
Aymara
az
Azerbaijani
ba
Bashkir
be
Belarusian
bg
Bulgarian
bh
Bihari
bi
Bislama
bm
Bambara
bn
Bengali
bo
Tibetan
br
Breton
bs
Bosnian
ca
Catalan
ce
Chechen
ch
Chamorro
co
Corsican
cr
Cree
cs
Czech
cu
Church Slavic
cv
Chuvash
cy
Welsh
da
Danish
de
German
dv
Divehi
dz
Dzongkha
ee
Ewe
el
Greek
en
English
eo
Esperanto
es
Spanish
et
Estonian
eu
Basque
fa
Persian
ff
Fulah
fi
Finnish
fj
Fijian
fo
Faroese
fr
French
fy
Western Frisian
ga
Irish
gd
Scottish Gaelic
gl
Galician
gn
Guaraní
gu
Gujarati
gv
Manx
ha
Hausa
he
Hebrew
hi
Hindi
ho
Hiri Motu
hr
Croatian
ht
Haitian
hu
Hungarian
hy
Armenian
hz
Herero
ia
Interlingua (International Auxiliary Language Association)
id
Indonesian
ie
Interlingue
ig
Igbo
ii
Sichuan Yi
ik
Inupiaq
io
Ido
is
Icelandic
it
Italian
iu
Inuktitut
ja
Japanese
jv
Javanese
ka
Georgian
kg
Kongo
ki
Kikuyu
kj
Kwanyama
kk
Kazakh
kl
Kalaallisut
km
Khmer
kn
Kannada
ko
Korean
kr
Kanuri
ks
Kashmiri
ku
Kurdish
kv
Komi
kw
Cornish
ky
Kirghiz
la
Latin
lb
Luxembourgish
lg
Ganda
li
Limburgish
ln
Lingala
lo
Lao
lt
Lithuanian
lu
Luba-Katanga
lv
Latvian
mg
Malagasy
mh
Marshallese
mi
Māori
mk
Macedonian
ml
Malayalam
mn
Mongolian
mo
Moldavian
mr
Marathi
ms
Malay
mt
Maltese
my
Burmese
na
Nauru
nb
Norwegian Bokmål
nd
North Ndebele
ne
Nepali
ng
Ndonga
nl
Dutch
nn
Norwegian Nynorsk
no
Norwegian
nr
South Ndebele
nv
Navajo
ny
Chichewa
oc
Occitan
oj
Ojibwa
om
Oromo
or
Oriya
os
Ossetian
pa
Panjabi
pi
Pāli
pl
Polish
ps
Pashto
pt
Portuguese
qu
Quechua
rm
Raeto-Romance
rn
Kirundi
ro
Romanian
ru
Russian
rw
Kinyarwanda
sa
Sanskrit
sc
Sardinian
sd
Sindhi
se
Northern Sami
sg
Sango
sh
Serbo-Croatian
si
Sinhala
sk
Slovak
sl
Slovenian
sm
Samoan
sn
Shona
so
Somali
sq
Albanian
sr
Serbian
ss
Swati
st
Southern Sotho
su
Sundanese
sv
Swedish
sw
Swahili
ta
Tamil
te
Telugu
tg
Tajik
th
Thai
ti
Tigrinya
tk
Turkmen
tl
Tagalog
tn
Tswana
to
Tonga
tr
Turkish
ts
Tsonga
tt
Tatar
tw
Twi
ty
Tahitian
ug
Uighur
uk
Ukrainian
ur
Urdu
uz
Uzbek
ve
Venda
vi
Vietnamese
vo
Volapük
wa
Walloon
wo
Wolof
xh
Xhosa
yi
Yiddish
yo
Yoruba
za
Zhuang
zh
Chinese
zu
Zulu
"""

SEARCH_URL = ('https://www.bing.com/search?q={{query}}%20language:{l.code}'
              '&go=Submit&qs=n&form=QBRE&filt=all&pq='
              '{{query}}%20language:{l.code}&sc=8-6&sp=-1&sk=')
SUGGEST_URL = ('http://api.bing.com/osjson.aspx?query='
               '{{query}}&language={l.code}')

# superset of Lang
Bing = namedtuple('Bing', 'name code')


def lang2search(l):
    """Convert `Lang` to search `dict`."""
    desc = u'Bing ({})'.format(l.name)
    return mkvariant(l.code.lower(),
                     l.name, desc,
                     SEARCH_URL.format(l=l),
                     SUGGEST_URL.format(l=l),
                     )


def main():
    """Print Wikipedia engine JSON to STDOUT."""
    data = mkdata(u'Bing', u'General search engine')

    lines = LANGS.strip().split('\n')
    i = 0
    while i < len(lines):
        t = Bing(lines[i + 1], lines[i])
        data['variants'].append(lang2search(t))
        i += 2

    print(json.dumps(data,
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
