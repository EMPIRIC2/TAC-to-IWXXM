#!/usr/bin/env bash
# workspaceOpen — load engineering-memory plugin for this workspace only.
set -euo pipefail
python3 -c 'import json; print(json.dumps({"pluginPaths": ["/Users/bigme/Documents/GitHub/spec-dev-knowledge-graph/cursor-plugin"]}))'
