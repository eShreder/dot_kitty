"""Custom tab bar for kitty: smart titles, SSH detection, command icons."""

import re
from kitty.boss import get_boss
from kitty.fast_data_types import Screen
from kitty.tab_bar import DrawData, ExtraData, TabBarData, as_rgb

# Colors (matching current catppuccin-style theme)
BG = as_rgb(0x11111B)
ACTIVE_BG = as_rgb(0xBAA0E8)
ACTIVE_FG = as_rgb(0x1E1E2E)
INACTIVE_BG = as_rgb(0x5C6370)
INACTIVE_FG = as_rgb(0xCDD6F4)
SSH_BG = as_rgb(0xF38BA8)       # red-pink for SSH (active)
SSH_INACTIVE_BG = as_rgb(0x7F5465)  # muted for SSH (inactive)

LEFT_SEP = "\ue0b6"   #
RIGHT_SEP = "\ue0b4"  #
MAX_TITLE_LENGTH = 30

# Command → emoji mapping
CMD_ICONS = {
    "vim": "\uf15c",
    "nvim": "\uf15c",
    "python": "\U0001f40d",   # 🐍
    "python3": "\U0001f40d",
    "node": "\u2b22",         # ⬢
    "docker": "\U0001f433",   # 🐳
    "git": "\ue725",
    "htop": "\U0001f4ca",     # 📊
    "top": "\U0001f4ca",
    "make": "\u2699",         # ⚙
    "cargo": "\U0001f980",    # 🦀
    "go": "\U0001f439",
    "claude": "\u2728",       # ✨
}

# SSH flags that consume the next argument
_SSH_OPT_FLAGS = set("bcDeFIiJlLmOopQRSWw")


def _find_ssh_host(tab: TabBarData) -> str | None:
    """If the tab is running SSH, extract and return the short hostname."""
    try:
        boss = get_boss()
        if not boss:
            return None

        real_tab = None
        for tm in boss.all_tab_managers:
            for t in tm:
                if t.id == tab.tab_id:
                    real_tab = t
                    break
            if real_tab:
                break

        if not real_tab or not real_tab.active_window:
            return None

        w = real_tab.active_window
        for fp in w.child.foreground_processes:
            cmdline = fp.get("cmdline", [])
            if not cmdline:
                continue
            exe = cmdline[0].rsplit("/", 1)[-1]
            if exe != "ssh":
                continue

            # Parse ssh arguments to find the destination host
            args = cmdline[1:]
            skip_next = False
            for arg in args:
                if skip_next:
                    skip_next = False
                    continue
                if arg.startswith("-"):
                    if len(arg) == 2 and arg[1] in _SSH_OPT_FLAGS:
                        skip_next = True
                    continue
                # First positional arg = [user@]host
                host = arg
                if "@" in host:
                    host = host.split("@", 1)[1]
                return host.split(".")[0]
    except Exception:
        pass
    return None


def _clean_title(title: str, ssh_host: str | None) -> tuple[str, bool]:
    """Return (display_title, is_ssh)."""
    if not title:
        title = "shell"

    if ssh_host:
        # Strip redundant "user@host:" / "host:" prefix from remote PS1 title
        cleaned = re.sub(
            r"^[\w-]+@" + re.escape(ssh_host) + r"[^:]*:\s*", "", title
        )
        cleaned = re.sub(
            r"^" + re.escape(ssh_host) + r"[^:]*:\s*", "", cleaned
        )
        if not cleaned:
            cleaned = title
        # Truncate the remote part
        if len(cleaned) > 18:
            cleaned = cleaned[:17] + "…"
        return f"🌐 {ssh_host}:{cleaned}", True

    # --- Local tab ---
    # Detect SSH in title as fallback (before connection completes)
    ssh_match = re.match(
        r"^ssh\s+(?:[-]\S+\s+)*(?:\w+@)?([^\s:]+)", title
    )
    if ssh_match:
        host = ssh_match.group(1).split(".")[0]
        return f"🌐 {host}", True

    # Extract command basename
    parts = title.split()
    cmd = parts[0].rsplit("/", 1)[-1]

    # Add icon if known
    icon = CMD_ICONS.get(cmd)
    if icon:
        display = f"{icon} {cmd}"
    elif len(title) > MAX_TITLE_LENGTH:
        display = cmd
    else:
        display = title

    # Final truncation
    if len(display) > MAX_TITLE_LENGTH:
        display = display[: MAX_TITLE_LENGTH - 1] + "…"

    return display, False


def draw_tab(
    draw_data: DrawData,
    screen: Screen,
    tab: TabBarData,
    before: int,
    max_tab_length: int,
    index: int,
    is_last: bool,
    extra_data: ExtraData,
) -> int:
    ssh_host = _find_ssh_host(tab)
    title, is_ssh = _clean_title(tab.title, ssh_host)
    is_active = tab.is_active

    # Pick colors
    if is_ssh:
        tab_bg = SSH_BG if is_active else SSH_INACTIVE_BG
        tab_fg = ACTIVE_FG
    elif is_active:
        tab_bg = ACTIVE_BG
        tab_fg = ACTIVE_FG
    else:
        tab_bg = INACTIVE_BG
        tab_fg = INACTIVE_FG

    content = f" ({index}) {title} "

    # Clamp to max length (account for separators + trailing space)
    overhead = 3  # left sep + right sep + space
    max_content = max_tab_length - overhead
    if max_content < 4:
        max_content = 4
    if len(content) > max_content:
        content = content[: max_content - 1] + "…"

    # Left separator (colored arrow on BG)
    screen.cursor.fg = tab_bg
    screen.cursor.bg = BG
    screen.draw(LEFT_SEP)

    # Tab body
    screen.cursor.fg = tab_fg
    screen.cursor.bg = tab_bg
    if is_active:
        screen.cursor.bold = True
    screen.draw(content)
    if is_active:
        screen.cursor.bold = False

    # Right separator
    screen.cursor.fg = tab_bg
    screen.cursor.bg = BG
    screen.draw(RIGHT_SEP)

    # Trailing space
    screen.cursor.fg = 0
    screen.cursor.bg = BG
    screen.draw(" ")

    return screen.cursor.x
