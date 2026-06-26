#!/usr/bin/env zsh
# shellcheck shell=bash disable=SC1090,SC1091,SC2148
# Setup fzf
# ---------
if [[ ! "$PATH" == *"$HOME/.local/fzf/bin"* ]]; then
  PATH="${PATH:+${PATH}:}$HOME/.local/fzf/bin"
fi

source <(fzf --zsh)
