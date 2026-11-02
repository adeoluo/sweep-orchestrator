# Records docs/demo/importance.gif from a real run: `vhs docs/demo/importance.tape` from the repo root.
Output docs/demo/importance.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 460
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' && uv sync -q && source .venv/bin/activate && clear` Enter
Sleep 10s
Show
Type `python -m sweep_orchestrator importance` Enter
Sleep 2s
Type `python -m sweep_orchestrator pareto` Enter
Sleep 3s
