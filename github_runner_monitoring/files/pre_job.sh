#!/bin/bash
set -euo pipefail
OUTFILE="./.job_metadata.json"
START_TIME_MS=$(date +%s%3N)
cat > "$OUTFILE" <<EOF
{
  "repo": "${GITHUB_REPOSITORY:-null}",
  "workflow": "${GITHUB_WORKFLOW:-null}",
  "run_id": "${GITHUB_RUN_ID:-null}",
  "run_number": "${GITHUB_RUN_NUMBER:-null}",
  "job_name": "${GITHUB_JOB:-null}",
  "actor": "${GITHUB_ACTOR:-null}",
  "event_name": "${GITHUB_EVENT_NAME:-null}",
  "start_time_ms": $START_TIME_MS
}
EOF
