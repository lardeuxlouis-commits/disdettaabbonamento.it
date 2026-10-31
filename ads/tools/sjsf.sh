#!/bin/zsh
# usage: sjsf.sh /path/to/file.js  -> runs the JS file in the Safari tab matching $TABKEY
K="${TABKEY:-/local/business/}"
osascript - "$1" "$K" <<'AS'
on run argv
  set js to read (POSIX file (item 1 of argv)) as «class utf8»
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
