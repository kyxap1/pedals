#!/usr/bin/env bash
# Indexes the manuals with Pagefind and puts a search button at the top of each
# manual's contents menu (desktop side nav and mobile TOC).
# Usage: build-search.sh <site dir>
set -euo pipefail

site=${1:?usage: build-search.sh <site dir>}
# The root catalog has its own filter; archived index-<year>.html pages would
# duplicate every hit.
manuals=("$site"/*/index.html)

# Sub-results link only to headings with an id. The convention puts section ids
# on the heading; this catches a section that still carries its own.
perl -0777 -pi -e 's{<section\b([^>]*?)\s+id="([^"]+)"([^>]*)>((?:(?!</?section\b|<h[1-6]\b).)*)<(h[1-6])\b((?![^>]*\bid=)[^>]*)>}{<section$1$3>$4<$5 id="$2"$6>}gs' "${manuals[@]}"

export PF_HEAD='<link href="../pagefind/pagefind-component-ui.css" rel="stylesheet"><script src="../pagefind/pagefind-component-ui.js" type="module"></script><style>pagefind-modal-trigger{display:block;margin-bottom:1.5rem}</style>'
export PF_TRIGGER='<pagefind-modal-trigger placeholder="Search"></pagefind-modal-trigger>'
export PF_MODAL='<pagefind-modal></pagefind-modal>'
# The <title> names the pedal on every page; the first h1 is often a wordmark image.
# Each manual gets its own directory name as a "pedal" filter and forces that
# filter on its own search instance, so a manual's search box only searches
# itself; the root page's search stays unfiltered across all manuals.
perl -pi -e '
  my ($slug) = $ARGV =~ m{([^/]+)/index\.html$};
  s|<main id="main-doc"|$& data-pagefind-body data-pagefind-filter="pedal:$slug"|;
  s|<title>|<title data-pagefind-meta="title">|;
  s|</head>|$ENV{PF_HEAD}</head>|;
  s|<div class="nav-container">|$&$ENV{PF_TRIGGER}|;
  s|id="toc-mobile"[^>]*>|$&$ENV{PF_TRIGGER}|;
  s|</body>|$ENV{PF_MODAL}<script type="module">window.PagefindComponents.getInstanceManager().getInstance("default").triggerFilters({ pedal: ["$slug"] });</script></body>|;
' "${manuals[@]}"

npx -y pagefind@1.5.2 --site "$site" --glob '*/index.html' --exclude-selectors '#toc-mobile'
