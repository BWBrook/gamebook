#!/bin/zsh
cd -- "${0:A:h}"
export PATH="/opt/homebrew/bin:$HOME/.local/bin:$PATH"
exec uv run python -m tools.reader_server --open
