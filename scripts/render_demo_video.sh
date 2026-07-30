#!/usr/bin/env bash
# Render a truthful local draft video from repeatable project evidence.
# This is not a submission-ready video until its owner reviews it, adds
# narration, and uploads it publicly under the event's requirements.
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="$project_root/.artifacts"
work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT
mkdir -p "$output_dir"

font="$(fc-match -f '%{file}' monospace | head -n 1)"
render_slide() {
  local name="$1"
  local title="$2"
  local body="$3"
  magick -size 1920x1080 xc:'#101827' \
    -font "$font" -fill '#f8fafc' -gravity north -pointsize 62 \
    -annotate +0+120 "$title" \
    -fill '#cbd5e1' -gravity center -pointsize 34 \
    -annotate +0+70 "$body" \
    -fill '#94a3b8' -gravity south -pointsize 24 \
    -annotate +0+70 'DRAFT VIDEO — review before public upload' \
    "$work_dir/$name.png"
}

render_slide 01-title 'Lineage Draft Agent' \
  'A review-only migration draft grounded in DataHub metadata\n\nNo warehouse access. No executed migration.'
render_slide 02-fixture 'Safe, repeatable demonstration' \
  'OFFLINE FIXTURE ONLY\n\nThe demo runs the project GraphQL parsing and draft logic locally.\nIt writes a packet with dataset URN, schema-derived SQL, lineage, and reviewed: false.'
render_slide 03-mcp 'Real DataHub MCP evidence' \
  'GitHub Actions run 30581519213 passed end-to-end:\n\nofficial quickstart → public showcase data → official MCP server → review draft\n\nThe run read a real dataset with 11 fields. No migration was executed.'
render_slide 04-review 'Human review remains required' \
  'Every SQL output begins with REVIEW REQUIRED.\n\nThe reviewer can inspect the dataset URN and upstream lineage\nbefore deciding whether any migration should be run.'

ffmpeg -y \
  -loop 1 -t 8 -i "$work_dir/01-title.png" \
  -loop 1 -t 10 -i "$work_dir/02-fixture.png" \
  -loop 1 -t 10 -i "$work_dir/03-mcp.png" \
  -loop 1 -t 9 -i "$work_dir/04-review.png" \
  -filter_complex '[0:v][1:v][2:v][3:v]concat=n=4:v=1:a=0,format=yuv420p[v]' \
  -map '[v]' -r 30 -movflags +faststart "$output_dir/lineage-draft-agent-demo-draft.mp4"

echo "Rendered $output_dir/lineage-draft-agent-demo-draft.mp4"
