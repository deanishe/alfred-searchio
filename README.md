Searchio! workflow for Alfred
=============================

Auto-suggest search results from multiple search engines and languages.

![Searchio! Demo][demo]


Contents
--------

<!-- MarkdownTOC autolink="true" bracket="round" depth="3" autoanchor="true" -->

- [Download and installation](#download-and-installation)
- [Usage](#usage)
    - [Configuration](#configuration)
    - [Importing Searches](#importing-searches)
- [Adding Engines](#adding-engines)
- [Licensing, thanks](#licensing-thanks)

<!-- /MarkdownTOC -->

Supports the following search engines/websites:

- Amazon
- Bing
- DuckDuckGo
- eBay
- Google
- Google Images
- Google Maps (requires a Google Places API key)
- Naver
- Wikia (only the top ~200 wikis, but you can [import](#importing-searches) any others)
- Wikipedia
- Wiktionary
- Yandex
- YouTube
- **plus** it can [import a search configuration](#importing-searches) from *any* website that supports OpenSearch autosuggestions


<a name="download-and-installation"></a>
Download and installation
-------------------------

Download the latest version from the [GitHub releases page](https://github.com/deanishe/alfred-searchio/releases/latest).


<a name="usage"></a>
Usage
-----

There are several example searches pre-configured:

- `g` — Search Google in English
- `gd` — Search Google in German
- `w` — Search the English Wikipedia
- `wd` — Search the German Wikipedia
- `yt` — Search the United States version of YouTube
- `ytd` — Search the German version of YouTube


<a name="configuration"></a>
### Configuration ###

There is a single variable in the workflow configuration screen (open the workflow in Alfred Preferences and hit the `[𝒙]` button): `GOOGLE_PLACES_API_KEY`. You must set this to use Google Maps search. You can get an API key [here](https://developers.google.com/places/web-service/get-api-key).

- `searchio [<query>]` — Show workflow settings
    - `Update Available …` — Shown if there is a new version of the workflow available to download. Action the item to install it.
    - `Installed Searches …` — View and delete your configured searches
    - `All Engines …` — View supported engines and add new searches
    - `Import Search …` — Import a new search configuration from a URL (see [Importing Searches](#importing-searches))
    - `Reload` — Regenerate the workflow's Script Filters from your configured searches (and clean the cache). Run this if you screw up the Script Filters or an update overwrites them.
    - `Online Help` — Open this page in your browser.
    - `Workflow up to Date` — You have the latest version of the workflow. Action this item to force a check for a new version.


<a name="importing-searches"></a>
### Importing Searches ###

Searchio! has the ability to import a search configuration from any website that supports the OpenSearch autosuggestion API.

Run `searchio` > `Import Search …` and the workflow will offer to import a search from a URL on your clipboard, the frontmost Safari tab or the frontmost Chrome tab.

It will try to find and read the OpenSearch description at the URL and import it (and the website's icon if available), then ask you to assign a keyword for the search.

**NOTE**: Although many websites support OpenSearch, few support the autosuggestion API that Searchio! uses. Sites based on MediaWiki usually support the API, so you can add all your favourite Wikia wikis (the built-in Wikia engine only supports the few hundred most popular wikis).


<a name="adding-engines"></a>
Adding Engines
--------------

TODO

<a name="licensing-thanks"></a>
## Licensing, thanks ##

The code in this workflow is released under the [MIT Licence](http://opensource.org/licenses/MIT).

The icons belong to the respective search engines and websites.

This workflow uses the [Alfred-Workflow](http://www.deanishe.net/alfred-workflow/) library and [docopt](http://docopt.org/) (both MIT-licensed).


[demo]: ./docs/demo.gif
