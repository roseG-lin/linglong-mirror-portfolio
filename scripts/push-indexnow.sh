#!/usr/bin/env bash
# IndexNow 主动推送：部署后向 Bing / Yandex / Seznam 等引擎秒级通告 URL 变更
# 用法：bash scripts/push-indexnow.sh
# 可选：BAIDU_TOKEN=xxx bash scripts/push-indexnow.sh  同步推送百度普通收录
set -euo pipefail
cd "$(dirname "$0")/.."

KEY="$(tr -d '[:space:]' < indexnow-key.txt)"
HOST="www.remifei.cn"
URLS=(
  "https://www.remifei.cn/"
  "https://www.remifei.cn/llms.txt"
  "https://www.remifei.cn/llms-full.txt"
  "https://www.remifei.cn/os/"
  "https://www.remifei.cn/case/01-huodai-platform.html"
  "https://www.remifei.cn/case/02-rag-pipeline.html"
  "https://www.remifei.cn/case/03-miku-privacy.html"
  "https://www.remifei.cn/case/04-reyes-video.html"
  "https://www.remifei.cn/case/05-yisheng-engine.html"
  "https://www.remifei.cn/case/06-novel-engine.html"
  "https://www.remifei.cn/case/07-mirror-value.html"
  "https://www.remifei.cn/case/08-shiyang-solver.html"
  "https://www.remifei.cn/case/09-longjob-pipeline.html"
)

URL_JSON="$(printf '"%s",' "${URLS[@]}" | sed 's/,$//')"
printf '{"host":"%s","key":"%s","keyLocation":"https://%s/%s.txt","urlList":[%s]}' \
  "$HOST" "$KEY" "$HOST" "$KEY" "$URL_JSON" > .indexnow-body.json

echo "== IndexNow push: ${#URLS[@]} URLs =="
HTTP_CODE="$(curl -sS -o .indexnow-resp.txt -w '%{http_code}' -X POST \
  -H 'Content-Type: application/json; charset=utf-8' \
  --data-binary @.indexnow-body.json \
  "https://api.indexnow.org/indexnow" || true)"
echo "HTTP $HTTP_CODE  body: $(cat .indexnow-resp.txt 2>/dev/null || echo '(empty)')"
case "$HTTP_CODE" in
  200|202) echo "IndexNow: accepted" ;;
  *) echo "IndexNow: NOT accepted (see https://indexnow.org/documentation)" >&2 ;;
esac
rm -f .indexnow-body.json .indexnow-resp.txt

if [ -n "${BAIDU_TOKEN:-}" ]; then
  echo "== Baidu push =="
  printf '%s\n' "${URLS[@]}" | curl -sS -X POST \
    "http://data.zz.baidu.com/urls?site=${HOST}&token=${BAIDU_TOKEN}" \
    -H 'Content-Type: text/plain' --data-binary @-
else
  echo "== Baidu push skipped (set BAIDU_TOKEN to enable) =="
fi
