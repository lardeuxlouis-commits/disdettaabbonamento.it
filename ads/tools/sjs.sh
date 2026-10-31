#!/bin/zsh
# usage: sjs.sh 'js'  -> runs in the Safari tab whose URL contains $TABKEY (default: /local/business/)
K="${TABKEY:-/local/business/}"
osascript - "$1" "$K" <<'AS'
on run argv
  set js to item 1 of argv
  set k to item 2 of argv
  tell application "Safari"
    repeat with w in windows
      repeat with t in tabs of w
        if (URL of t as text) contains k then
          return do JavaScript js in t
        end if
      end repeat
    end repeat
  end tell
  return "NOTAB"
end run
AS
