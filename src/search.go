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

	"github.com/NodePrime/jsonpath"
	aw "github.com/deanishe/awgo"
	"github.com/deanishe/awgo/util"
)

var (
	maxAge                = time.Second * 900
	searchID, query       string
	searchesDir, cacheDir string
	// HTTPTimeout is the timeout for establishing an HTTP(S) connection.
	HTTPTimeout = (60 * time.Second)
	wf          *aw.Workflow
)

func init() {
	wf = aw.New()
	searchesDir = filepath.Join(wf.DataDir(), "searches")
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

	if r.StatusCode > 299 {
		return nil, fmt.Errorf("[%d] %s", r.StatusCode, r.Status)
	}

	data, err := ioutil.ReadAll(r.Body)
	if err != nil {
		return nil, err
	}

	log.Printf("response=%s", data)

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
			// log.Printf("r=%s", r.Value)
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

	log.Printf("querying \"%s\" for \"%s\" ...", s.Title, q)
	reload := func() (interface{}, error) { return searchServer(s, q) }
	if err := wf.Cache.LoadOrStoreJSON(name, maxAge, reload, &words); err != nil {
		return err
	}

	// Send results to Alfred
	for _, word := range words {
		wf.NewItem(word).
			Subtitle(s.Title).
			Arg(s.SearchURLForQuery(word)).
			Icon(&aw.Icon{Value: s.Icon}).
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

func main() {
	wf.Run(run)
}
