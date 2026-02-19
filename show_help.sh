#!/usr/bin/env bash
# Kitty keybindings cheat sheet — shown as overlay

bold='\033[1m'
dim='\033[2m'
accent='\033[38;5;141m'
key='\033[38;5;183m'
reset='\033[0m'
sep="${dim}────────────────────────────────────────────${reset}"

printf "\n"
printf "  ${bold}${accent}Kitty Keybindings${reset}\n"
printf "  ${sep}\n\n"

printf "  ${bold}${accent}Tabs${reset}\n"
printf "  ${key}  alt + 1…9${reset}          switch to tab N\n"
printf "  ${key}  ctrl + t${reset}            new tab\n"
printf "  ${key}  ctrl + w${reset}            close tab\n"
printf "  ${key}  ctrl+shift + pgup${reset}   move tab left\n"
printf "  ${key}  ctrl+shift + pgdn${reset}   move tab right\n"
printf "\n"

printf "  ${bold}${accent}Splits${reset}\n"
printf "  ${key}  ctrl+shift + -${reset}      split horizontal ─\n"
printf "  ${key}  ctrl+shift + \\\\${reset}      split vertical │\n"
printf "  ${key}  ctrl+shift + w${reset}      close pane\n"
printf "  ${key}  ctrl+shift + ←↑↓→${reset}  navigate panes\n"
printf "  ${key}  ctrl+alt  + ←↑↓→${reset}   resize panes\n"
printf "  ${key}  ctrl+shift + z${reset}      zoom / unzoom pane\n"
printf "\n"

printf "  ${bold}${accent}General${reset}\n"
printf "  ${key}  cmd+ctrl + m${reset}        toggle maximized\n"
printf "  ${key}  ctrl+shift + f5${reset}     reload config\n"
printf "  ${key}  cmd+shift + /${reset}       this help\n"
printf "\n"
printf "  ${sep}\n"
printf "  ${dim}Press any key to close...${reset}\n"

read -n 1 -s -r
