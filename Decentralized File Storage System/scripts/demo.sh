#!/bin/bash
set -euo pipefail
#set x

# Configuration constants
readonly REPO="project-a-series-of-tubes"
readonly MY_UNI="rdn2108"
readonly MY_KEY="$HOME/.ssh/csee4119-s24"
readonly NODES=("35.239.66.54" "35.202.218.139" "34.172.121.79" "34.71.33.207")
readonly TRACKER=${NODES[0]}
readonly PEERS=("${NODES[@]:1:3}")
readonly MAGIC_PORT=60006

declare -a PORTS
for ((i=0; i<4; i++)); do
  PORTS[i]=$((MAGIC_PORT + i))
done

success() { printf "\033[92mSuccess: %s\033[0m\n" "${1}" >&2; }
info()    { printf "\033[94mInfo: %s\033[0m\n" "${1}" >&2; }
warn()    { printf "\033[91mWarning: %s\033[0m\n" "${1}" >&2; }

# Tmux command execution helper
tmuxecute() { info "pane $1: $2"; tmux send-keys -t "$1" "$2" C-m; }

ssh_into_vms() {
  for i in {1..4}; do
    tmuxecute "$i" "ssh -i $MY_KEY $MY_UNI@${NODES[${i}-1]}"
  done
}

update_repo="cd ${REPO}; git stash; git pull"
kill_em_all="pkill -f 'peer' || true; pkill -f 'tracker' || pkill -f 'flask' || true"
start_tracker="python -m blocktubes.tracker ${MAGIC_PORT} &"
start_peers="python -m blocktubes.peer --tracker_host $TRACKER --tracker_port $MAGIC_PORT &"
start_flask="flask run --port=${PORTS[\$((pane-1))]}"

execute_commands() {
  local panes=("$@")
  local command="${panes[-1]}"
  unset 'panes[-1]'
  for pane in "${panes[@]}"; do tmuxecute "$pane" "$command"; done
}

exe_peers() { execute_commands 1 2 3 "$@"; }
exe_tracker() { execute_commands 4 "$@"; }
exe_all() { execute_commands 1 2 3 4 "$@"; }

main() {
  ssh_into_vms
  exit
  sleep 2
  exe_all "$update_repo"
  sleep 1
  exe_all "$kill_em_all"
  sleep 1
  exe_tracker "$kill_tracker"
  exe_tracker "$start_tracker"
  exe_peers "$start_peers"
}

main
