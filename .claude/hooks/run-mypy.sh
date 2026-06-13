#!/bin/bash
INPUT=$(cat)

# Claude Code Edit/Write payload
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_response.filePath // empty' 2>/dev/null)
if [[ -n "$FILE" && "$FILE" == *.py ]]; then
    mypy "$FILE" --ignore-missing-imports 2>/dev/null || true
    exit 0
fi

# Codex apply_patch payload — extract .py files from patch headers
echo "$INPUT" | jq -r '.tool_input.patch // empty' 2>/dev/null \
    | grep -E '^\*\*\* (Update|Add) File:' \
    | sed 's/.*File: //' \
    | grep '\.py$' \
    | while read -r f; do
        [[ -f "$f" ]] && mypy "$f" --ignore-missing-imports 2>/dev/null || true
    done
