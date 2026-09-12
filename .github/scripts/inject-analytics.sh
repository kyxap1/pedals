#!/usr/bin/env bash
# Adds the Google Analytics and Cloudflare Web Analytics tags to every page of
# the built site, so new manuals are tracked without editing their HTML.
# Usage: inject-analytics.sh <site dir>
set -euo pipefail

site=${1:?usage: inject-analytics.sh <site dir>}
: "${GA_MEASUREMENT_ID:?set repo variable GA_MEASUREMENT_ID}"
: "${CF_BEACON_TOKEN:?set repo variable CF_BEACON_TOKEN}"

export GTAG="<script async src=\"https://www.googletagmanager.com/gtag/js?id=$GA_MEASUREMENT_ID\"></script><script>window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', '$GA_MEASUREMENT_ID');</script>"
export CF_BEACON="<script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{\"token\": \"$CF_BEACON_TOKEN\"}'></script>"

find "$site" -name '*.html' -exec perl -pi -e 's|</head>|$ENV{GTAG}</head>|; s|</body>|$ENV{CF_BEACON}</body>|' {} +
