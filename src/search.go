//
// Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
//
// MIT Licence. See http://opensource.org/licenses/MIT
//
// Created on 2017-12-11
//

// Command search performs a web search based on a Searchio! search.
package main

import (
	"crypto/md5"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"time"

	"golang.org/x/net/html/charset"

	"github.com/JumboInteractiveLimited/jsonpath"
	aw "github.com/deanishe/awgo"
	"github.com/deanishe/awgo/util"
)

var (
	maxAge                = time.Second * 900
	queryInResults        bool // Also add query to results
	alfredSortsResults    bool // Turn off UIDs
	searchID, query       string
	searchesDir, cacheDir string
	// HTTPTimeout is the timeout for establishing an HTTP(S) connection.
	HTTPTimeout = (60 * time.Second)
	wf          *aw.Workflow
)

func init() {
	wf = aw.New()
	queryInResults = wf.Config.GetBool("SHOW_QUERY_IN_RESULTS")
	alfredSortsResults = wf.Config.GetBool("ALFRED_SORTS_RESULTS")
	searchesDir = filepath.Join(wf.DataDir(), "searches")

	if !alfredSortsResults {
		wf.Configure(aw.SuppressUIDs(true))
	}
}

// GetenvBool returns a boolean based on an environment/workflow variable.
// "1", "yes" = true, "0", "no", empty = false
func GetenvBool(key string) bool {
	s := strings.ToLower(os.Getenv(key))
	switch s {
	case "":
		return false
	case "0":
		return false
	case "no":
		return false
	case "1":
		return true
	case "yes":
		return true
	}
	log.Printf("[WARNING] don't understand value \"%s\" for \"%s\", returning false", s, key)
	return false
}

// Search is a Searchio! search configuration.
type Search struct {
	Icon          string `json:"icon"`
	Jsonpath      string `json:"jsonpath"`
	Keyword       string `json:"keyword"`
	PercentEncode bool   `json:"pcencode"`
	SearchURL     string `json:"search_url"`
	SuggestURL    string `json:"suggest_url"`
	Title         string `json:"title"`
	UID           string `json:"uid"`
}

// SearchURLForQuery returns a URL for query based on SearchURL template.
func (s *Search) SearchURLForQuery(q string) string { return s.makeURL(q, s.SearchURL) }

// SuggestURLForQuery returns a URL for query based on SuggestURL template.
func (s *Search) SuggestURLForQuery(q string) string { return s.makeURL(q, s.SuggestURL) }

// Escape query as path or query string depending on Search.PercentEncode.
func (s *Search) escapeQuery(q string) string {
	if s.PercentEncode {
		return url.PathEscape(q)
	} else {
		return url.QueryEscape(q)
	}
}

func (s *Search) makeURL(q, baseURL string) string {
	q = s.escapeQuery(q)
	u := strings.Replace(baseURL, "{query}", q, -1)
	// Also replace envvars
	return os.Expand(u, func(key string) string { return s.escapeQuery(os.Getenv(key)) })
}

// makeHTTPClient returns an http.Client with a sensible configuration.
func makeHTTPClient() http.Client {
	return http.Client{
		Transport: &http.Transport{
			Dial: (&net.Dialer{
				Timeout:   HTTPTimeout,
				KeepAlive: HTTPTimeout,
			}).Dial,
			TLSHandshakeTimeout:   30 * time.Second,
			ResponseHeaderTimeout: 30 * time.Second,
			ExpectContinueTimeout: 10 * time.Second,
		},
	}
}

// Load a search from the corresponding configuration file in the searches directory.
func loadSearch(id string) (*Search, error) {
	p := filepath.Join(searchesDir, id+".json")
	log.Printf("loading search from %s ...", p)
	b, err := ioutil.ReadFile(p)
	if err != nil {
		return nil, err
	}
	s := &Search{}
	if err := json.Unmarshal(b, &s); err != nil {
		return nil, err
	}
	s.UID = id
	return s, nil
}

func decodeResponse(r *http.Response) ([]byte, error) {
	data, err := ioutil.ReadAll(r.Body)
	if err != nil {
		return nil, err
	}
	enc, name, ok := charset.DetermineEncoding(data, r.Header.Get("Content-Type"))
	log.Printf("enc=%v, name=%s, ok=%v", enc, name, ok)

	data, err = enc.NewDecoder().Bytes(data)
	if err != nil {
		return nil, err
	}
	return data, nil
}

// Query server.
func searchServer(s *Search, q string) ([]string, error) {
	var (
		client = makeHTTPClient()
		u      = s.SuggestURLForQuery(q)
		words  = []string{}
	)

	r, err := client.Get(u)
	if err != nil {
		return nil, err
	}
	defer r.Body.Close()
	log.Printf("[%d] %s", r.StatusCode, r.Status)

	if r.StatusCode > 299 {
		return nil, fmt.Errorf("[%d] %s", r.StatusCode, r.Status)
	}

	data, err := decodeResponse(r)
	if err != nil {
		return nil, err
	}

	// Append + as we want to extract a value, not a path
	jp := s.Jsonpath
	if jp[len(jp)-1] != '+' {
		jp += "+"
	}
	paths, err := jsonpath.ParsePaths(jp)
	if err != nil {
		return nil, fmt.Errorf("bad JSON path: %v", err)
	}

	eval, err := jsonpath.EvalPathsInBytes(data, paths)
	if err != nil {
		return nil, fmt.Errorf("JSON parse error: %v", err)
	}

	for {
		r, ok := eval.Next()
		if !ok {
			break
		}
		if r != nil {
			var word string
			if err := json.Unmarshal(r.Value, &word); err != nil {
				return nil, err
			}
			words = append(words, word)
		}
	}
	if eval.Error != nil {
		return nil, fmt.Errorf("couldn't unmarshal JSON: %v", eval.Error)
	}

	return words, nil
}

// Perform search and show results in Alfred.
func doSearch(s *Search, q string) error {
	var (
		h      = fmt.Sprintf("%x", md5.Sum([]byte(q)))
		reldir = fmt.Sprintf("searches/%s/%s/%s", s.UID, h[:2], h[2:4])
		name   = fmt.Sprintf("%s/%s.json", reldir, h)
		words  = []string{}
	)
	util.MustExist(filepath.Join(wf.CacheDir(), reldir))

	log.Printf(`querying "%s" for "%s" ...`, s.Title, q)
	reload := func() (interface{}, error) { return searchServer(s, q) }
	if err := wf.Cache.LoadOrStoreJSON(name, maxAge, reload, &words); err != nil {
		return err
	}

	log.Printf(`%d results for "%s"`, len(words), q)

	// Send results to Alfred
	var (
		// querySeen bool
		icon = &aw.Icon{Value: s.Icon}
	)
	for _, word := range words {
		if strings.ToLower(word) == strings.ToLower(q) && queryInResults {
			continue
		}
		URL := s.SearchURLForQuery(word)
		wf.NewItem(word).
			Subtitle(s.Title).
			Autocomplete(word + " ").
			Arg(URL).
			UID(URL).
			Icon(icon).
			Valid(true)
	}

	// Add query at end of results
	if queryInResults || len(words) == 0 {
		URL := s.SearchURLForQuery(q)
		wf.NewItem(q).
			Subtitle(s.Title).
			Autocomplete(q + " ").
			Arg(URL).
			UID(URL).
			Icon(icon).
			Valid(true)
	}

	wf.WarnEmpty("No Results", "Try a different query?")
	wf.SendFeedback()
	return nil
}

// Entry point.
func run() {
	argv := wf.Args()
	if len(argv) < 2 {
		log.Fatalln("usage: search <search> <query>")
	}
	searchID, query = argv[0], argv[1]
	s, err := loadSearch(searchID)
	if err != nil {
		wf.FatalError(err)
	}

	if err := doSearch(s, query); err != nil {
		wf.FatalError(err)
	}
}

// Run via Workflow.Run to catch panics.
func main() {
	wf.Run(run)
}
