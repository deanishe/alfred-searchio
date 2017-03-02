#!/usr/bin/env zsh

count=10
wordfile=/usr/share/dict/words

here="$( cd "$( dirname "$0" )"; pwd )"
searchio="$here/../src/searchio"

log() {
  echo "$@" >&2
}


usage() {
    cat <<EOS
bench.zsh [options]

Usage:
    bench.zsh [-c <num>]
    bench.zsh -h

Options:
    -c      Run each benchmark this many times
    -h      Show this help message and exit
EOS
}

while getopts ":c:h" opt; do
  case $opt in
    c)
      count=$OPTARG
      ;;
    h)
      usage
      exit 0
      ;;
    \?)
      log "Invalid option: -$OPTARG"
      exit 1
      ;;
  esac
done
shift $((OPTIND-1))

words=( $( python -c "import random, sys; sys.stdout.write(''.join(random.sample(open('$wordfile').readlines(), $count)))") )

log 'benching searchio ...'
total=0.0
for w in $words; do
  start=$( date +%s.%N )
  $searchio search google-en "$w" &>/dev/null
  now=$( date +%s.%N )
  elapsed=$( echo "$now - $start" | bc )
  total=$( echo "$elapsed + $total" | bc)
  log "${elapsed}s"
done

per=$( echo "scale=3; $total / $count" | bc )
log "searchio: $count in ${total}s (${per}s/run)"


log 'benching cURL ...'
total=0.0
url='https://suggestqueries.google.com/complete/search?client=firefox&ds=i&hl=en&safe=off&q='
for w in $words; do
  start=$( date +%s.%N )
  curl -sSL "${url}${w}" &>/dev/null
  now=$( date +%s.%N )
  elapsed=$( echo "$now - $start" | bc )
  total=$( echo "$elapsed + $total" | bc)
  log "${elapsed}s"
done

per=$( echo "scale=3; $total / $count" | bc )
log "cURL: $count in ${total}s (${per}s/run)"

