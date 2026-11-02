# Records docs/demo/http.gif from a real run: `vhs docs/demo/http.tape` from the repo root.
Output docs/demo/http.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 440
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' && uv sync -q && source .venv/bin/activate` Enter
Sleep 2s
Type `python -m sweep_orchestrator serve --port 18328 >/dev/null 2>&1 &` Enter
Sleep 2s
Sleep 8.0s
Type `clear` Enter
Sleep 1s
Show
Type `curl -s localhost:18328/sweep -d '{"count": 27}' | jq -c '.strategies[]'` Enter
Sleep 3s
Type `curl -s localhost:18328/pareto -d '{"points": [[0.1, 0.9], [0.3, 0.3], [0.5, 0.6], [0.8, 0.1]]}' | jq -c` Enter
Sleep 3s
Hide
Type `kill %1` Enter
Sleep 1s
