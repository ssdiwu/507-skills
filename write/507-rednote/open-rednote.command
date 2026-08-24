#!/bin/zsh
set -euo pipefail

skill_dir="${0:A:h}"

if (( $# >= 1 )); then
  work_dir="${1:A}"
else
  work_dir=$(osascript -e 'POSIX path of (choose folder with prompt "选择包含 raw.md 的作品目录")')
  work_dir="${work_dir%/}"
fi

project_dir="$work_dir/小红书"
source_path="$work_dir/raw.md"

if [[ -f "$project_dir/content.md" ]]; then
  exec python3 "$skill_dir/scripts/serve_rednote.py" --project "$project_dir"
fi

if [[ ! -f "$source_path" ]]; then
  source_path=$(osascript -e 'POSIX path of (choose file with prompt "选择 Markdown 主稿")')
fi

exec python3 "$skill_dir/scripts/serve_rednote.py" --project "$project_dir" --source "$source_path"
