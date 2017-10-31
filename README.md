# Searchio! workflow for Alfred #

Auto-suggest search results from multiple search engines and languages.

![Searchio! Demo][demo]


Supports the following search engines/websites:

- Google
- Google Images
- Google Maps
- YouTube
- Wikipedia
- Wiktionary
- Amazon
- eBay
- DuckDuckGo
- Bing
- Yahoo!
- Ask.com
- Yandex.ru
- Naver.com
- Wikia.com
- Kinopoisk.ru


## Download and installation ##

Download the latest version from the [GitHub releases page](https://github.com/deanishe/alfred-searchio/releases/latest) or [Packal](http://www.packal.org/workflow/searchio).

## Usage ##

There are several searches pre-configured. Only some have keywords (i.e. can be used as-is):

- `g` — Search Google in system (i.e. default) language
- `m` — Search Google Maps in system (i.e. default) language
- `gi` — Search Google Images in system (i.e. default) language
- `w` — Search Wikipedia in system (i.e. default) language
- `wn` — Search Wiktionary in system (i.e. default) language
- `a` — Search Amazon in system (i.e. default) language. If your system language is English, this will search  Amazon.com. Use `-l uk` in the Script Filter to search Amazon.co.uk or `-l ca` to search Amazon.ca.
- `yt` — Search YouTube in system (i.e. default) language
- `searchio [<query>]` — Show settings and list of supported search engines. Currently, the only setting is a toggle to also show the `<query>` in the results list (default: `No`).
- `searchiohelp` — Open help (this README) in your browser

Most of the other available search engines also have an example Script Filter configured, but without a keyword. Add a keyword if you wish to use one of the examples.

Several of the Script Filters demonstrate the use of the `--lang` (or `-l`) option to the `search.py` script to search in a different language/region. See [the Languages section](#languages) for more information.

To add a new search, either copy/paste an existing Script Filter, or create a new one as follows:

![][screen1]

**Note:** Be sure to select the same escaping options as in the screenshot (Backquotes, Double Quotes, Backslashes, Dollars).

By default, your system language will be used. To specify a custom language:

![][screen2]

**Note:** Be sure to connect the Script Filter to the Open URL action or it won't work.

## Icons ##

Icons for each search engine can be found in the `icons` subirectory of the Workflow.

## Languages ##

The `-l` or `--lang` argument to `search.py` doesn't follow any hard-and-fast rules: it depends on the search engine you're using. With some search engines (Google, Wikipedia, Wiktionary, Bing, DuckDuckGo), it's a language, e.g. `uk` = Ukrainian. In others (Yahoo!, Amazon, Ask), it's treated as a region, e.g. `uk` = United Kingdom.

Some search engines (Bing, DuckDuckGo, eBay) do not provide language-specific suggestions, but actioning the result will open a list of language-specific results in your browser.

## Search engines ##

The following search engines are supported. Pass the `ID` to the `-e`/`--engine` argument of `search.py` to search using that engine. If `--engine` is not specified, Google will be used.

|       ID      |      Name     |
|---------------|---------------|
| amazon        | Amazon        |
| ask           | Ask           |
| bing          | Bing          |
| ddg           | DuckDuckGo    |
| ebay          | eBay          |
| google        | Google        |
| google-images | Google Images |
| google-maps   | Google Maps   |
| naver         | Naver.com     |
| wikia         | Wikia         |
| wikipedia     | Wikipedia     |
| wiktionary    | Wiktionary    |
| yahoo         | Yahoo!        |
| yandex        | Yandex.ru     |
| youtube       | YouTube       |
| kinopoisk     | Kinopoisk.ru  |


### Wikipedia, Wiktionary ###

The `--lang` argument will be treated as a subdomain, e.g. `de` will retrieve results from `de.wikipedia.org`.

### Google ###

The `--lang` argument should work for [any language supported by Google](https://www.google.com/preferences#languages), with the obvious exceptions of things like Klingon and Hacker…

### Bing, DuckDuckGo, eBay ###

Bing, eBay and DuckDuckGo do not provide language-specific suggestions, but the results opened in your browser should be restricted to the specified language/region.

### Ask, Amazon, Yahoo! ###

Ask.com, Amazon and Yahoo! do not provide language-specific search suggestions/results, but rather region-specific ones. In many cases, this won't make a difference (e.g. `--lang de` and `--lang fr` will provide German and French results respectively), however the behaviour is different in some cases, e.g. `uk` means "United Kingdom", not "Ukrainian".

### Wikia.com ###

Wikia.com is a special case. Instead of languages or regions, the `--lang` option is used to set a specific wiki, e.g. `--lang gameofthrones` will search `gameofthrones.wikia.com`.

You *must* specify a `--lang` option for Wikia searches.

## Examples ##

Use these in the `Script` field of a Script Filter.

```bash
# Google (default engine) in your system (default) language
/usr/bin/python search.py "{query}"

# Google in German
/usr/bin/python search.py -l de "{query}"

# Google in French
/usr/bin/python search.py -l fr "{query}"

# YouTube in Brazilian Portuguese
/usr/bin/python search.py -e youtube -l pt-BR "{query}"

# Amazon.co.uk
/usr/bin/python search.py -e amazon -l uk "{query}"

# Amazon.ca
/usr/bin/python search.py -e amazon -l ca "{query}"

# DuckDuckGo in system (default) language
/usr/bin/python search.py -e ddg "{query}"

# DuckDuckGo in Spanish
/usr/bin/python search.py -e ddg -l es "{query}"

# Yahoo! UK
/usr/bin/python search.py -e yahoo -l uk "{query}"

# Yahoo! Australia
/usr/bin/python search.py -e yahoo -l au "{query}"

# Wikipedia in Simple English
/usr/bin/python search.py -e wikipedia -l simple "{query}"

# Wikipedia in Polish
/usr/bin/python search.py -e wikipedia -l pl "{query}"

# Wiktionary in Spanish
/usr/bin/python search.py -e wiktionary -l es "{query}"

# Game of Thrones wiki at Wikia.com
/usr/bin/python search.py -e wikia -l gameofthrones "{query}"

# Borderlands wiki at Wikia.com
/usr/bin/python search.py -e wikia -l borderlands "{query}"
```

## Licensing, thanks ##

The code in this workflow is released under the [MIT Licence](http://opensource.org/licenses/MIT).

The icons belong to the respective search engines and websites.

This workflow uses the [Alfred-Workflow](http://www.deanishe.net/alfred-workflow/) library and [docopt](http://docopt.org/) (both MIT-licensed).


[demo]: ./docs/demo.gif
[screen1]: http://www.deanishe.net/alfred-searchio/screen1.png
[screen2]: http://www.deanishe.net/alfred-searchio/screen2.png
