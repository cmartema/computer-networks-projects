#!/bin/bash
readonly SESSION="test_tubes"

reset_tmux() {
    tmux kill-session -t "$SESSION" 2> /dev/null || true
    tmux new-session -d -s "$SESSION" \; \
         split-window -h \; \
         split-window -v -t "${SESSION}:0.0" \; \
         split-window -v -t "${SESSION}:0.1" \; \
         split-window -v -t "${SESSION}:0.3"
    echo "tmux session ${SESSION} reset and configured"
}

[[ -n "$TMUX" ]] && echo "This script should not be run inside tmux" && exit 1

reset_tmux

read -p "Attach to tmux session ${SESSION}? [y/n] " -n 1 -r
echo
[[ $REPLY =~ ^[Yy]$ ]] && tmux attach-session -t "$SESSION"
