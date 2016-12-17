#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-01
#

"""Google search as Python plugin."""

from __future__ import absolute_import, print_function


from searchio.engines import Engine

LANGUAGES = {
    'ach': u'Acoli',
    'af': u'Afrikaans',
    'ak': u'Akan',
    'am': u'\u12a0\u121b\u122d\u129b',
    'ar': u'\u0627\u0644\u0639\u0631\u0628\u064a\u0629',
    'az': u'az\u0259rbaycan dili',
    'ban': u'Balinese',
    'be': u'\u0431\u0435\u043b\u0430\u0440\u0443\u0441\u043a\u0430\u044f',
    'bem': u'Ichibemba',
    'bg': u'\u0431\u044a\u043b\u0433\u0430\u0440\u0441\u043a\u0438',
    'bn': u'\u09ac\u09be\u0982\u09b2\u09be',
    'br': u'brezhoneg',
    'bs': u'bosanski',
    'ca': u'catal\xe0',
    'ceb': u'Cebuano',
    'chr': u'\u13e3\u13b3\u13a9',
    'ckb': u'Central Kurdish',
    'co': u'Corsican',
    'crs': u'Seychellois Creole',
    'cs': u'\u010de\u0161tina',
    'cy': u'Cymraeg',
    'da': u'dansk',
    'de': u'Deutsch',
    'ee': u'E\u028begbe',
    'el': u'\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac',
    'en': u'English',
    'eo': u'esperanto',
    'es': u'espa\xf1ol',
    'es-419': u'espa\xf1ol (Latinoam\xe9rica)',
    'et': u'eesti',
    'eu': u'euskara',
    'fa': u'\u0641\u0627\u0631\u0633\u06cc',
    'fi': u'suomi',
    'fo': u'f\xf8royskt',
    'fr': u'fran\xe7ais',
    'fy': u'West-Frysk',
    'ga': u'Gaeilge',
    'gaa': u'Ga',
    'gd': u'G\xe0idhlig',
    'gl': u'galego',
    'gn': u'Guarani',
    'gu': u'\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0',
    'ha': u'Hausa',
    'haw': u'\u02bb\u014clelo Hawai\u02bbi',
    'hi': u'\u0939\u093f\u0928\u094d\u0926\u0940',
    'hr': u'hrvatski',
    'ht': u'Haitian Creole',
    'hu': u'magyar',
    'hy': u'\u0570\u0561\u0575\u0565\u0580\u0565\u0576',
    'ia': u'Interlingua',
    'id': u'Indonesia',
    'ig': u'Igbo',
    'is': u'\xedslenska',
    'it': u'italiano',
    'iw': u'\u05e2\u05d1\u05e8\u05d9\u05ea',
    'ja': u'\u65e5\u672c\u8a9e',
    'jw': u'Javanese',
    'ka': u'\u10e5\u10d0\u10e0\u10d7\u10e3\u10da\u10d8',
    'kg': u'Kongo',
    'kk': u'\u049b\u0430\u0437\u0430\u049b \u0442\u0456\u043b\u0456',
    'km': u'\u1781\u17d2\u1798\u17c2\u179a',
    'kn': u'\u0c95\u0ca8\u0ccd\u0ca8\u0ca1',
    'ko': u'\ud55c\uad6d\uc5b4',
    'kri': u'Krio (Sierra Leone)',
    'ky': u'\u043a\u044b\u0440\u0433\u044b\u0437\u0447\u0430',
    'la': u'Latin',
    'lg': u'Luganda',
    'ln': u'ling\xe1la',
    'lo': u'\u0ea5\u0eb2\u0ea7',
    'loz': u'Lozi',
    'lt': u'lietuvi\u0173',
    'lua': u'Luba-Lulua',
    'lv': u'latvie\u0161u',
    'mfe': u'kreol morisien',
    'mg': u'Malagasy',
    'mi': u'Maori',
    'mk': u'\u043c\u0430\u043a\u0435\u0434\u043e\u043d\u0441\u043a\u0438',
    'ml': u'\u0d2e\u0d32\u0d2f\u0d3e\u0d33\u0d02',
    'mn': u'\u043c\u043e\u043d\u0433\u043e\u043b',
    'mr': u'\u092e\u0930\u093e\u0920\u0940',
    'ms': u'Bahasa Melayu',
    'mt': u'Malti',
    'my': u'\u1017\u1019\u102c',
    'ne': u'\u0928\u0947\u092a\u093e\u0932\u0940',
    'nl': u'Nederlands',
    'nn': u'nynorsk', 'no': u'norsk',
    'nso': u'Northern Sotho',
    'ny': u'Nyanja',
    'nyn': u'Runyankore',
    'oc': u'Occitan',
    'om': u'Oromoo',
    'or': u'\u0b13\u0b21\u0b3c\u0b3f\u0b06',
    'pa': u'\u0a2a\u0a70\u0a1c\u0a3e\u0a2c\u0a40',
    'pcm': u'Nigerian Pidgin',
    'pl': u'polski',
    'ps': u'\u067e\u069a\u062a\u0648',
    'pt-BR': u'portugu\xeas (Brasil)',
    'pt-PT': u'portugu\xeas (Portugal)',
    'qu': u'Runasimi',
    'rm': u'rumantsch',
    'rn': u'Ikirundi',
    'ro': u'rom\xe2n\u0103',
    'ru': u'\u0440\u0443\u0441\u0441\u043a\u0438\u0439',
    'rw': u'Kinyarwanda',
    'sd': u'Sindhi',
    'si': u'\u0dc3\u0dd2\u0d82\u0dc4\u0dbd',
    'sk': u'sloven\u010dina',
    'sl': u'sloven\u0161\u010dina',
    'sn': u'chiShona',
    'so': u'Soomaali',
    'sq': u'shqip',
    'sr': u'\u0441\u0440\u043f\u0441\u043a\u0438',
    'sr-Latn': u'srpski (latinica)',
    'sr-ME': u'srpski (Crna Gora)',
    'st': u'Southern Sotho',
    'su': u'Sundanese',
    'sv': u'svenska',
    'sw': u'Kiswahili',
    'ta': u'\u0ba4\u0bae\u0bbf\u0bb4\u0bcd',
    'te': u'\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41',
    'tg': u'Tajik',
    'th': u'\u0e44\u0e17\u0e22',
    'ti': u'\u1275\u130d\u122d\u129b',
    'tk': u'Turkmen',
    'tl': u'Filipino',
    'tlh': u'Klingon',
    'tn': u'Tswana',
    'to': u'lea fakatonga',
    'tr': u'T\xfcrk\xe7e',
    'tt': u'Tatar',
    'tum': u'Tumbuka',
    'tw': u'Twi',
    'ug': u'\u0626\u06c7\u064a\u063a\u06c7\u0631\u0686\u06d5',
    'uk': u'\u0443\u043a\u0440\u0430\u0457\u043d\u0441\u044c\u043a\u0430',
    'ur': u'\u0627\u0631\u062f\u0648',
    'uz': u'o\u2018zbek',
    'vi': u'Ti\u1ebfng Vi\u1ec7t',
    'wo': u'Wolof',
    'xh': u'Xhosa',
    'yi': u'\u05d9\u05d9\u05b4\u05d3\u05d9\u05e9',
    'yo': u'\xc8d\xe8 Yor\xf9b\xe1',
    'zh-CN': u'\u4e2d\u6587 (\u7b80\u4f53)',
    'zh-TW': u'\u4e2d\u6587 (\u7e41\u9ad4)',
    'zu': u'isiZulu',
}


# class Google(Engine):
#     """Get search suggestions from Google."""

#     @property
#     def id(self):
#         return 'googlepy'

#     @property
#     def name(self):
#         return 'GooglePy'

#     @property
#     def suggest_url(self):
#         return 'https://suggestqueries.google.com/complete/search?client=firefox&q={query}&hl={variant}'

#     @property
#     def search_url(self):
#         return 'https://www.google.com/search?q={query}&hl={hl}&safe=off'

#     @property
#     def variants(self):
#         return {
#             'en': {
#                 'name': 'English',
#                 'vars': { 'hl': 'en' },
#             },
#             'de': {
#                 'name': 'Deutsch',
#                 'vars': { 'hl': 'de' },
#             },
#         }
