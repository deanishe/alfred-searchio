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
        - [Workflow Configuration Sheet](#workflow-configuration-sheet)
        - [In-Workflow Configuration](#in-workflow-configuration)
    - [Importing Searches](#importing-searches)
- [Adding Engines](#adding-engines)
- [Licensing, thanks](#licensing-thanks)

<!-- /MarkdownTOC -->

Supports the following search engines/websites:

- Amazon
- Bing
- DuckDuckGo
- DuckDuckGo Image Search
- eBay
- Google
- Google "I'm Feeling Lucky"
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

The workflow is configured via the `searchio` keyword and some [workflow variables](https://www.alfredapp.com/help/workflows/advanced/variables/) set in the workflow configuration sheet.


<a name="workflow-configuration-sheet"></a>
#### Workflow Configuration Sheet ####

There are some variables in the workflow configuration screen (open the workflow in Alfred Preferences and hit the `[𝒙]` button):

|           Name          |                                                                                                    Description                                                                                                    |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ALFRED_SORTS_RESULTS`  | Set to `1` or `yes` to enable Alfred's knowledge. Set to `0` or `no` to always show results in the order returned by the API.                                                                                     |
| `GOOGLE_PLACES_API_KEY` | You must set this to use Google Maps search. You can get an API key [here](https://developers.google.com/places/web-service/get-api-key).                                                                         |
| `SHOW_QUERY_IN_RESULTS` | Set to `1` or `yes` to always append the entered query to the end of the results (so you can hit `↑` to select it). If unset (or set to `0` or `no`), the query will only be shown if there are no other results. |


<a name="in-workflow-configuration"></a>
#### In-Workflow Configuration ####

- `searchio [<query>]` — Show workflow settings
    - `Update Available …` — Shown if there is a new version of the workflow available to download. Action the item to install it.
    - `Installed Searches …` — View and delete your configured searches
    - `All Engines …` — View supported engines and add new searches
    - `Import Search …` — Import a new search configuration from a URL (see [Importing Searches](#importing-searches))
    - `Reload` — Regenerate the workflow's Script Filters from your configured searches (and clean the cache). Run this if you screw up the Script Filters or an update overwrites them.
    - `Show Query in Results` — Turn the option to show the query you entered in the results on/off. The query is added to the end of the results, so you can hit `↑` to go straight to it. The query is always shown if there are no other results.
    - `Alfred Sorts Results` — Turns Alfred's knowledge on/off. If on,
    Alfred remembers which result you chose for which query and moves
    that result to the top. If off, results are always shown in the
    order they are returned by the API. If on, `Show Query in Results`
    cannot guarantee that the query is always the last result.
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

In addition to the built-in engines, you can add your own definitions in the `engines` folder in the workflow's data directory. (Enter `searchio workflow:opendata` to open the data folder in Finder.)

An engine definition looks like this:

```json
{
  "description": "Alternative search engine",
  "jsonpath": "$[*].phrase",
  "title": "DuckDuckGo Images",
  "pcencode": false,
  "variants": [
    {
      "name": "Argentina",
      "search_url": "https://duckduckgo.com/?iax=images&ia=images&kp=-2&kz=-1&kl=ar-es&q={query}",
      "suggest_url": "https://duckduckgo.com/ac/?kp=-2&kz=-1&kl=ar-es&q={query}",
      "title": "DuckDuckGo Images Argentina",
      "uid": "ar-es"
    }
  ]
}
```

`title` and `description` are self-explanatory. `jsonpath` is the JSON path expression that extracts the search suggestions from the JSON returned by the suggestion API.

The optional `pcencode` field tells Searchio! to percent-encode the search query rather than use plus-encoding (the default).

`variants` define the actual searches supported by the search engine, typically one per region or language. All fields are required. `suggest_url` points to the autosuggestion endpoint and `search_url` is the URL of the search results that should be opened in the browser. Both URLs must contain the `{query}` placeholder, which is replaced with the user's search query.

The (optional) icon for your custom engine should be placed in the `icons` directory alongside the `engines` one. It should have the same basename as the engine definition file, just with a different file extension. Supported icon extensions are `png`, `icns`, `jpg` and `jpeg`.

<a name="licensing-thanks"></a>
## Licensing, thanks ##

The code in this workflow is released under the [MIT Licence](http://opensource.org/licenses/MIT).

The icons belong to the respective search engines and websites.

This workflow uses the following libraries:

- [Alfred-Workflow](https://www.deanishe.net/alfred-workflow/)
- [AwGo](https://github.com/deanishe/awgo/)
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)
- [docopt](http://docopt.org/)
- [jsonpath-rw](https://pypi.org/project/jsonpath-rw/)

[demo]: ./docs/demo.gif
