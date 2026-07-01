#!/usr/bin/env bash
# security-gate.sh — pre-launch security scanner for vibe-coded apps.
#
# Runs the MECHANICAL half of the 30-minute pre-launch checklist: the things a
# machine can verify (leaked secrets, tracked .env files, keys in the frontend,
# wildcard CORS, missing RLS, debug statements). The MANUAL half (privacy policy,
# auth failure-case testing, rate limits, etc.) lives in SECURITY-CHECKLIST.md and
# is confirmed by the pre-push hook.
#
# Usage:
#   security-gate.sh            # gate mode: exit 2 if anything CRITICAL/HIGH is found
#   security-gate.sh --report   # report mode: print findings, always exit 0
#
# Tune false positives with a .security-gate-allow file (one ERE per line; any
# finding whose "path:line:content" matches a line there is dropped).
#
# Deep-history secret scanning is out of scope here — pair this with gitleaks or
# trufflehog in CI if you need to scan past commits.

set -u

MODE="${1:-gate}"

# --- colors (disabled when not a tty) ---------------------------------------
if [ -t 1 ]; then
  R=$'\033[31m'; Y=$'\033[33m'; G=$'\033[32m'; B=$'\033[1m'; DIM=$'\033[2m'; X=$'\033[0m'
else
  R=""; Y=""; G=""; B=""; DIM=""; X=""
fi

CRIT=0; HIGH=0; WARN=0
CRIT_LINES=""; HIGH_LINES=""; WARN_LINES=""

# Repo root (run from anywhere)
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "${R}Not inside a git repository.${X}"; exit 1
}
cd "$ROOT" || exit 1

ALLOW_FILE="$ROOT/.security-gate-allow"

# Shared excludes: build output, lockfiles, minified bundles, the gate's own files.
EXCLUDES=(
  ":(exclude)*-lock.*" ":(exclude)package-lock.json" ":(exclude)yarn.lock"
  ":(exclude)pnpm-lock.yaml" ":(exclude)*.min.js" ":(exclude)*.min.css"
  ":(exclude)*.map" ":(exclude)**/dist/**" ":(exclude)**/build/**"
  ":(exclude)**/.next/**" ":(exclude)**/node_modules/**" ":(exclude)**/vendor/**"
  ":(exclude)SECURITY-CHECKLIST.md" ":(exclude).security-gate-allow"
  ":(exclude)scripts/security-gate.sh" ":(exclude).githooks/pre-push"
)

# ggrep <regex> [extra-pathspec...] -> path:line:content for tracked files
ggrep() {
  local re="$1"; shift
  git grep -nIE "$re" -- . "${EXCLUDES[@]}" "$@" 2>/dev/null
}

# drop lines matched by the allowlist (comment/blank lines in it are ignored)
filter_allow() {
  if [ -f "$ALLOW_FILE" ] && grep -qvE '^[[:space:]]*(#|$)' "$ALLOW_FILE" 2>/dev/null; then
    grep -vE -f <(grep -vE '^[[:space:]]*(#|$)' "$ALLOW_FILE") 2>/dev/null || true
  else
    cat
  fi
}

# Low-risk paths: a secret-shaped string here is almost always a test fixture,
# doc placeholder, or API spec — not a live leak. Findings in these get
# downgraded to WARN (surfaced, not blocking). Real provider-key VALUE patterns
# still scan these paths globally, so a genuine key in a test is still caught.
LOWRISK_RE='(/|^|\.)tests?(/|\.)|(/|^)(spec|specs|__tests__|__mocks__|e2e|examples?|docs?|runbooks?|deploy|scripts|samples?)/|[Tt]ests?\.[A-Za-z]+$|\.(test|spec)\.[A-Za-z]+$|\.(md|mdx|example|sample|template|dist)$|(openapi|swagger)[^/]*\.(json|ya?ml)$|\.tfvars\.example$'

# _emit <severity> <label> <hits> [show_content] — formats + buckets one finding.
_emit() {
  local sev="$1" label="$2" hits="$3" show="${4:-0}"
  [ -z "$(printf '%s' "$hits" | tr -d '[:space:]')" ] && return 0
  local count loc out=""
  count="$(printf '%s\n' "$hits" | grep -c . )"
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    loc="$(printf '%s' "$line" | cut -d: -f1-2)"
    if [ "$show" = "1" ]; then
      out="${out}      ${DIM}${loc}${X}  $(printf '%s' "$line" | cut -d: -f3- | sed 's/^[[:space:]]*//' | cut -c1-80)
"
    else
      out="${out}      ${DIM}${loc}${X}
"
    fi
  done <<< "$(printf '%s\n' "$hits" | grep -v '^[[:space:]]*$' | head -n 12)"
  [ "$count" -gt 12 ] && out="${out}      ${DIM}... and $((count-12)) more${X}
"
  case "$sev" in
    CRIT) CRIT=$((CRIT+1)); CRIT_LINES="${CRIT_LINES}    ${R}✗ ${label}${X}
${out}";;
    HIGH) HIGH=$((HIGH+1)); HIGH_LINES="${HIGH_LINES}    ${Y}▲ ${label}${X}
${out}";;
    WARN) WARN=$((WARN+1)); WARN_LINES="${WARN_LINES}    ${Y}• ${label}${X}
${out}";;
  esac
}

# record <severity> <label> <hits> [show_content]
# Partitions hits by path: real source keeps <severity>; test/doc/example paths
# are downgraded to WARN so they never block a push.
record() {
  local sev="$1" label="$2" hits="$3" show="${4:-0}"
  [ -z "$hits" ] && return 0
  local base="" low="" path
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    path="${line%%:*}"
    if printf '%s' "$path" | grep -qiE "$LOWRISK_RE"; then
      low="${low}${line}
"
    else
      base="${base}${line}
"
    fi
  done <<< "$hits"
  _emit "$sev" "$label" "$base" "$show"
  [ "$sev" != "WARN" ] && _emit WARN "$label  ${DIM}(test/doc/example — review, non-blocking)${X}" "$low" "$show"
  [ "$sev" = "WARN" ] && _emit WARN "$label" "$low" "$show"
}

# scan <severity> <label> <regex> [pathspec...] — secrets: never show content
scan() {
  local sev="$1" label="$2" re="$3"; shift 3
  local hits; hits="$(ggrep "$re" "$@" | filter_allow)"
  record "$sev" "$label" "$hits" 0
}

echo
echo "${B}🔒 Security gate${X}  ${DIM}$(basename "$ROOT")${X}"
echo

# ===========================================================================
# 1. LEAKED SECRETS (CRITICAL — block). Path:line only, value never printed.
# ===========================================================================
scan CRIT "Anthropic API key"        'sk-ant-[A-Za-z0-9_-]{20,}'
scan CRIT "OpenAI API key"           'sk-(proj-)?[A-Za-z0-9]{20,}'
scan CRIT "Stripe live/test secret"  '[rs]k_(live|test)_[A-Za-z0-9]{20,}'
scan CRIT "AWS access key id"        'AKIA[0-9A-Z]{16}'
scan CRIT "Google API key"           'AIza[0-9A-Za-z_-]{35}'
scan CRIT "GitHub token"             '(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,}'
scan CRIT "Slack token"              'xox[baprs]-[A-Za-z0-9-]{10,}'
scan CRIT "Private key block"        '-----BEGIN [A-Z ]*PRIVATE KEY-----'
scan CRIT "Generic hardcoded secret" \
  '(api[_-]?key|secret[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token|password|passwd)["'"'"']?\s*[:=]\s*["'"'"'][^"'"'"'$<{][^"'"'"']{11,}["'"'"']'

# ===========================================================================
# 2. TRACKED .env FILES. .env / .env.local / *.local = CRITICAL (real secrets).
#    .env.development / .production / .test / .staging = WARN (framework
#    convention commits these for build-time public config). *.example = OK.
# ===========================================================================
ENV_ALL="$(git ls-files | grep -E '(^|/)\.env($|\.)' | grep -vE '\.(example|sample|template|dist)$' | filter_allow)"
ENV_CRIT="$(printf '%s\n' "$ENV_ALL" | grep -E '(^|/)\.env(\.local)?$|\.local$' || true)"
ENV_WARN="$(printf '%s\n' "$ENV_ALL" | grep -vE '(^|/)\.env(\.local)?$|\.local$' || true)"
record CRIT ".env file committed to git" "$ENV_CRIT" 0
record WARN ".env.<environment> committed (confirm it holds no secrets)" "$ENV_WARN" 0

# ===========================================================================
# 3. SECRET KEYS REACHABLE FROM THE BROWSER BUNDLE (WARN — weak signal).
#    A secret-key NAME in browser-bundle code (.ts/.tsx/.js/.jsx/.vue/.svelte).
#    .cs/.go/.py/.rb server files are never shipped to the browser, so they're
#    excluded. Config/env READS are the correct pattern, so they're filtered.
#    Real exposure (a secret VALUE, or a public-prefixed secret) is caught by
#    sections 1 and the env-prefix check below at higher severity.
# ===========================================================================
FE_HITS="$(git grep -nIE \
  'SERVICE_ROLE|service_role|STRIPE_SECRET|_SECRET_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|SECRET_ACCESS_KEY' \
  -- '*.ts' '*.tsx' '*.js' '*.jsx' '*.vue' '*.svelte' '*.astro' "${EXCLUDES[@]}" 2>/dev/null \
  | grep -vE 'process\.env|import\.meta\.env|//|/\*|^\s*\*|GetEnvironmentVariable|Configuration\[|config\[|[^A-Za-z]env\.|throw |Error\(|required|Missing' \
  | filter_allow )"
record WARN "Secret-key name in browser-bundle code (verify it isn't shipped to the client)" "$FE_HITS" 1

# A real VALUE assigned to a public-prefixed secret var = exposed in the bundle.
# Merely READING process.env.NEXT_PUBLIC_X_SECRET (or import.meta.env / ?? default)
# is the correct pattern, so reads and fallbacks are excluded.
PUB_SECRET="$(ggrep '(NEXT_PUBLIC_|VITE_|REACT_APP_)[A-Z0-9_]*(SECRET|SERVICE_ROLE|PRIVATE|API_KEY|PASSWORD)[A-Z0-9_]*\s*[:=]\s*["'"'"']?[^[:space:]"'"'"']{6,}' \
  | grep -vE 'process\.env|import\.meta\.env|getenv|\?\?|\$\{|[:=]\s*[<{]|process\[|configuration\[|config\[' | filter_allow)"
record HIGH "Hardcoded value on a public-prefixed secret var (ships to the browser)" "$PUB_SECRET" 1

# ===========================================================================
# 4. .gitignore HYGIENE (HIGH if .env not ignored).
# ===========================================================================
if [ ! -f .gitignore ]; then
  record HIGH "No .gitignore in repo" ".gitignore:0" 0
elif ! grep -qE '(^|/)\.env' .gitignore; then
  record HIGH ".env not listed in .gitignore" ".gitignore:0" 0
fi

# ===========================================================================
# 5. CORS WILDCARD (HIGH — flagged, block). Wide-open API origins.
# ===========================================================================
CORS_HITS="$(ggrep 'Access-Control-Allow-Origin["'"'"']?\s*[:,]\s*["'"'"']\*|origin\s*:\s*["'"'"']\*["'"'"']|cors\(\s*\)|AllowAnyOrigin\(\)' | filter_allow)"
record HIGH "Wildcard / wide-open CORS" "$CORS_HITS" 1

# ===========================================================================
# 6. SUPABASE RLS (WARN). Tables created but RLS never enabled in migrations.
# ===========================================================================
if [ -d supabase ] || git grep -qIE '@supabase/supabase-js' -- package.json 2>/dev/null; then
  if git grep -qiIE 'create table' -- 'supabase/**' '*.sql' 2>/dev/null; then
    if ! git grep -qiIE 'enable row level security' -- 'supabase/**' '*.sql' 2>/dev/null; then
      record WARN "Supabase tables found but no 'enable row level security' in any migration" \
        "supabase/migrations:0" 0
    fi
  fi
fi

# ===========================================================================
# 7. DEBUG / LEAKY ARTIFACTS (WARN). Not blocking, but clean before launch.
# ===========================================================================
DBG="$(ggrep 'console\.(log|debug)|debugger;|System\.out\.print|print\(.*DEBUG' \
       'src/' 'app/' 'lib/' 'components/' 2>/dev/null | filter_allow)"
record WARN "Debug statements (console.log / debugger / prints)" "$DBG" 1

STACK="$(ggrep 'printStackTrace|res\.(send|json)\(\s*err' | filter_allow)"
record WARN "Possible stack trace / raw error sent to client" "$STACK" 1

# ===========================================================================
# REPORT
# ===========================================================================
print_block() { [ -n "$1" ] && printf '%s\n' "$1"; }

if [ "$CRIT" -gt 0 ]; then
  echo "${R}${B}  CRITICAL ($CRIT)${X}  ${DIM}secrets / data exposure — must fix before push${X}"
  print_block "$CRIT_LINES"
fi
if [ "$HIGH" -gt 0 ]; then
  echo "${Y}${B}  HIGH ($HIGH)${X}  ${DIM}likely vulnerability — fix before launch${X}"
  print_block "$HIGH_LINES"
fi
if [ "$WARN" -gt 0 ]; then
  echo "${Y}${B}  WARN ($WARN)${X}  ${DIM}clean these up; not blocking${X}"
  print_block "$WARN_LINES"
fi

if [ "$CRIT" -eq 0 ] && [ "$HIGH" -eq 0 ] && [ "$WARN" -eq 0 ]; then
  echo "${G}  ✓ No automated security issues found.${X}"
fi
echo

# Exit contract: 2 = blocking findings, 0 = clean or warn-only / report mode.
if [ "$MODE" = "--report" ] || [ "$MODE" = "report" ]; then
  exit 0
fi
if [ "$CRIT" -gt 0 ] || [ "$HIGH" -gt 0 ]; then
  echo "${R}Blocked: resolve CRITICAL/HIGH findings, or allowlist false positives in .security-gate-allow${X}"
  echo "${DIM}Emergency bypass (use sparingly): git push --no-verify${X}"
  echo
  exit 2
fi
exit 0
