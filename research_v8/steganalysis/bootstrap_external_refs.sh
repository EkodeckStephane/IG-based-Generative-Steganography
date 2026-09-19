#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-research_v8/steganalysis/external_refs}"
mkdir -p "$ROOT"

clone_at () {
  local url="$1" dir="$2" sha="$3"
  if [ ! -d "$dir/.git" ]; then
    git clone --no-checkout "$url" "$dir"
  fi
  git -C "$dir" fetch --depth 1 origin "$sha"
  git -C "$dir" checkout --detach "$sha"
}

clone_at https://github.com/SiaStg/SiaStegNet.git "$ROOT/SiaStegNet" 592d9e13f39f287d9c675f1b89272bcfb6a9627c
clone_at https://github.com/albblgb/Deep-Steganalysis.git "$ROOT/Deep-Steganalysis" 1a5b8f88ce3c928e44ca22ad66010d23cd4a1262

echo "SiaStegNet: $(git -C "$ROOT/SiaStegNet" rev-parse HEAD)"
echo "Deep-Steganalysis: $(git -C "$ROOT/Deep-Steganalysis" rev-parse HEAD)"
