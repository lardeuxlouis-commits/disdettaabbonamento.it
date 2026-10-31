#!/bin/zsh
K="${TABKEY:-/local/business/}"
osascript - "$K" <<'AS'
on run argv
  set k to item 1 of argv
  tell application "Safari"
    repeat with w in windows
      repeat with t in tabs of w
        if (URL of t as text) contains k then
          set current tab of w to t
          set index of w to 1
          activate
          return "front"
        end if
      end repeat
    end repeat
  end tell
  return "NOTAB"
end run
AS
