#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
Sudoku (API + MRV Solver) — Countdown + Quick Peek + Instant Finish + Party + Music
===================================================================================

Big, dramatic 5→1 countdown, blazing "quick peek" placements, instant finish,
curtain reveal, and a celebratory emoji flood — with cheers sound and party music.

Install:
    pip install "requests>=2.31,<3" "rich>=13,<14" playsound

Note:
    Put a royalty-free audio file named `party.mp3` in the SAME folder as this script.
    For best sync, keep its length close to DANCE_SECONDS.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import platform
import threading
from collections import deque
from itertools import cycle
from typing import List, Optional, Tuple

# ======================= Config (you can tweak) =======================

COUNTDOWN_SECONDS   = 5        # big 5..1 digits
COUNTDOWN_PAUSE     = 1.2

DEFAULT_PEEK_SECONDS = 2.0     # visible "fast placements" burst
ANIM_DELAY           = 0.01
ANIM_EVERY_STEPS     = 1

CURTAIN_PAUSE        = 0.10
HIGHLIGHT_COLOR      = "yellow"

# Victory party settings
DANCE_SECONDS = 5.0            # try to match party.mp3 duration
DANCE_FPS     = 14
PARTY_WIDTH   = 60
PARTY_MUSIC_FILE  = "party.mp3"  # must be in same folder (or use absolute path)

DEFAULT_API_URL   = "https://youdosudoku.com/api/"

# Built-in offline fallback (classic puzzle + solution)
FALLBACK_PUZZLE = (
    "53..7...."
    "6..195..."
    ".98....6."
    "8...6...3"
    "4..8.3..1"
    "7...2...6"
    ".6....28."
    "...419..5"
    "....8..79"
)
FALLBACK_SOLUTION = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286179"
)

# ======================= Optional libraries =======================

# Rich terminal
RICH = False
console = None
box = None
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.align import Align
    from rich.live import Live
    from rich import box as rich_box

    console = Console()
    box = rich_box
    RICH = True
except Exception:
    RICH = False

# Windows beep
WINSOUND = None
try:
    if platform.system().lower().startswith("win"):
        import winsound
        WINSOUND = winsound
except Exception:
    WINSOUND = None

# MP3 playback
try:
    from playsound import playsound
except Exception:
    playsound = None

# ======================= Sound helpers =======================

def beep(freq: int = 800, dur_ms: int = 130) -> None:
    if WINSOUND:
        try:
            WINSOUND.Beep(freq, dur_ms)
        except Exception:
            pass

def play_party_music() -> None:
    """Play party.mp3 (blocking in this thread); call via a background thread."""
    if playsound and os.path.exists(PARTY_MUSIC_FILE):
        try:
            playsound(PARTY_MUSIC_FILE)
        except Exception as e:
            if RICH:
                console.print(f"[yellow]Music playback failed: {e}[/yellow]")
            else:
                print(f"Music playback failed: {e}")
    else:
        if RICH:
            console.print("[yellow]party.mp3 not found or playsound not installed[/yellow]")

# ======================= Render helpers =======================

def render_board(board: List[List[int]], title: str = "Sudoku",
                 highlight: Optional[Tuple[int, int]] = None):
    """Rich table if available; plain text otherwise."""
    if not RICH:
        lines = [title, "     " + "  ".join([f"C{c+1}" for c in range(9)])]
        for r in range(9):
            if r in (3, 6):
                lines.append("    " + "-" * 29)
            row = [f"R{r+1:<2} "]
            for c in range(9):
                if c in (3, 6):
                    row.append("| ")
                v = board[r][c]
                sym = str(v) if v else "."
                if highlight == (r, c):
                    sym = f"[{sym}]"
                row.append(sym + " ")
            lines.append("".join(row))
        return "\n".join(lines)

    t = Table(title=f"🧩 {title}", box=box.SQUARE, border_style="cyan", show_lines=True)
    t.add_column("", justify="center", style="dim")
    for c in range(9):
        t.add_column(f"C{c+1}", justify="center", style="white", no_wrap=True)
    for r in range(9):
        cells = [f"[dim]R{r+1}[/dim]"]
        for c in range(9):
            v = board[r][c]
            txt = str(v) if v else "[dim].[/dim]"
            color = "white" if ((r // 3) + (c // 3)) % 2 == 0 else "bright_black"
            cell = f"[{color}]{txt}[/{color}]"
            if highlight == (r, c):
                cell = f"[bold {HIGHLIGHT_COLOR}]{str(v) if v else '·'}[/bold {HIGHLIGHT_COLOR}]"
            cells.append(cell)
        t.add_row(*cells)
    return t

# ======================= Input / spinner =======================

def ask_for_difficulty() -> str:
    """Interactive difficulty picker (no default auto-selection)."""
    if RICH and sys.stdin.isatty():
        console.print(Panel.fit(
            "\n[b]Choose your challenge:[/b]  "
            "[green]easy[/green]  |  [yellow]medium[/yellow]  |  [red]hard[/red]",
            title="🎮 Sudoku Difficulty", border_style="cyan"
        ))
        while True:
            ans = Prompt.ask(
                "Type one",
                choices=["easy", "medium", "hard", "e", "m", "h"],
                show_default=False
            ).lower()
            if ans in ("e", "easy"):
                return "easy"
            if ans in ("m", "medium"):
                return "medium"
            if ans in ("h", "hard"):
                return "hard"
    else:
        # Plain prompt (no default)
        while True:
            txt = input("\nChoose difficulty (easy / medium / hard): ").strip().lower()
            if txt in ("e", "easy"):
                return "easy"
            if txt in ("m", "medium"):
                return "medium"
            if txt in ("h", "hard"):
                return "hard"
            print("Please type: easy, medium, or hard.")

def loading_dots(label: str = "Fetching puzzle", seconds: float = 1.2) -> None:
    if seconds <= 0:
        return
    seq = cycle([label, label + ".", label + "..", label + "..."])
    if RICH:
        with Live(Panel(next(seq), border_style="magenta", title="⏳ Please wait"),
                  refresh_per_second=12, console=console) as live:
            steps = int(seconds / 0.2)
            for _ in range(steps):
                live.update(Panel(next(seq), border_style="magenta", title="⏳ Please wait"))
                time.sleep(0.2)
    else:
        print(label, end="", flush=True)
        for _ in range(int(seconds / 0.2)):
            print(".", end="", flush=True)
            time.sleep(0.2)
        print()

# ======================= Puzzle I/O =======================

def normalize_board(obj) -> List[List[int]]:
    """Accept a 9x9 list or an 81-char string of digits/., and return a 9x9 int grid."""
    if isinstance(obj, list):
        grid = [[0 if str(x) in (".", "0") else int(x) for x in row] for row in obj]
        if len(grid) == 9 and all(len(r) == 9 for r in grid):
            return grid
    if isinstance(obj, str):
        digits = [(0 if ch in "0." else int(ch)) for ch in obj if ch in "0123456789."]
        if len(digits) == 81:
            return [digits[i * 9:(i + 1) * 9] for i in range(9)]
    raise ValueError(f"Unexpected puzzle format: {type(obj)}")

def fetch_puzzle(api_url: str, diff: str, timeout=(5, 20)) -> dict:
    import requests
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    body = {"difficulty": diff, "solution": True, "array": True}
    resp = requests.post(api_url, json=body, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

def get_puzzle_and_solution(api_url: str, difficulty: str, force_offline: bool = False):
    if force_offline:
        return normalize_board(FALLBACK_PUZZLE), normalize_board(FALLBACK_SOLUTION), difficulty
    try:
        data = fetch_puzzle(api_url, difficulty)
        board = normalize_board(data.get("puzzle"))
        sol = data.get("solution")
        solution = normalize_board(sol) if sol else None
        return board, solution, data.get("difficulty", difficulty)
    except Exception as e:
        if RICH:
            console.print(f"[yellow]API failed ({e}). Using offline fallback.[/yellow]")
        else:
            print(f"API failed ({e}). Using offline fallback.")
        return normalize_board(FALLBACK_PUZZLE), normalize_board(FALLBACK_SOLUTION), difficulty

# ======================= Big 5→1 Countdown =======================

BIG = {
    "5": ["████", "█   ", "███ ", "   █", "███ "],
    "4": ["█  █", "█  █", "████", "   █", "   █"],
    "3": ["███ ", "   █", " ██ ", "   █", "███ "],
    "2": ["███ ", "   █", "███ ", "█   ", "███ "],
    "1": ["  █ ", " ██ ", "  █ ", "  █ ", "████"],
}
PHRASES = {5: "Ready?", 4: "Here we go…", 3: "Brace yourself…", 2: "Focus…", 1: "And… ACTION!"}

def countdown(skip: bool = False) -> None:
    if skip:
        return
    if RICH:
        console.print(Panel.fit("Get ready…", border_style="magenta", title="🎬"))
        time.sleep(0.7)
        for n in range(COUNTDOWN_SECONDS, 0, -1):
            art = "\n".join(BIG[str(n)])
            console.clear()
            console.print(Panel(
                Align.center(
                    f"[bold cyan]{art}[/bold cyan]\n\n[bold]{PHRASES.get(n, '')}[/bold]\n[dim]Starting in {n}…[/dim]",
                    vertical="middle"),
                border_style="cyan", width=50, title="⏳ Countdown"
            ))
            beep(600 + (COUNTDOWN_SECONDS - n) * 120, 120)
            time.sleep(COUNTDOWN_PAUSE)
        console.clear()
    else:
        print("Get ready…")
        for n in range(COUNTDOWN_SECONDS, 0, -1):
            print(f"{PHRASES.get(n, '')} {n}")
            beep()
            time.sleep(COUNTDOWN_PAUSE)

# ======================= Solver (MRV) =======================

def solve_with_mrv(board: List[List[int]],
                   peek_seconds: float = DEFAULT_PEEK_SECONDS,
                   instant: bool = False) -> bool:
    """Backtracking solver with MRV and O(1) constraint sets + quick peek animation."""
    row_used = [set() for _ in range(9)]
    col_used = [set() for _ in range(9)]
    box_used = [set() for _ in range(9)]
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v:
                row_used[r].add(v)
                col_used[c].add(v)
                box_used[(r // 3) * 3 + (c // 3)].add(v)

    start_time = time.time()
    show_animation = bool(RICH and (not instant) and peek_seconds > 0.0)
    steps = 0
    current = None
    last_update = 0.0

    def candidates(r: int, c: int):
        used = row_used[r] | col_used[c] | box_used[(r // 3) * 3 + (c // 3)]
        return [n for n in range(1, 10) if n not in used]  # deterministic

    def find_mrv():
        best = None
        best_cands = None
        best_len = 10
        for rr in range(9):
            for cc in range(9):
                if board[rr][cc] == 0:
                    cs = candidates(rr, cc)
                    l = len(cs)
                    if l < best_len:
                        best, best_cands, best_len = (rr, cc), cs, l
                        if l == 1:
                            return best, best_cands
        return best, best_cands

    def place(r, c, n):
        board[r][c] = n
        row_used[r].add(n); col_used[c].add(n); box_used[(r//3)*3 + (c//3)].add(n)

    def unplace(r, c, n):
        board[r][c] = 0
        row_used[r].discard(n); col_used[c].discard(n); box_used[(r//3)*3 + (c//3)].discard(n)

    def maybe_update(live):
        nonlocal steps, last_update
        if not show_animation: return
        if (time.time() - start_time) > peek_seconds: return
        steps += 1
        if steps % ANIM_EVERY_STEPS == 0:
            now = time.time()
            if now - last_update >= ANIM_DELAY:
                live.update(render_board(board, title="Solving…", highlight=current))
                last_update = now

    def _solve(live=None):
        nonlocal current
        pos, cands = find_mrv()
        if pos is None:
            if live and show_animation and (time.time() - start_time) <= peek_seconds:
                live.update(render_board(board, title="Solved!", highlight=None))
                time.sleep(ANIM_DELAY)
            return True
        r, c = pos
        current = (r, c)
        for n in (cands or []):
            place(r, c, n)
            if live: maybe_update(live)
            if _solve(live): return True
            unplace(r, c, n)
            if live: maybe_update(live)
        return False

    if RICH and show_animation:
        with Live(render_board(board, title="Solving…"), console=console, refresh_per_second=30) as live:
            return _solve(live)
    else:
        return _solve()

# ======================= Curtain reveal =======================

def curtain_reveal(board: List[List[int]], pause: float = CURTAIN_PAUSE) -> None:
    if RICH:
        temp = [[0]*9 for _ in range(9)]
        with Live(render_board(temp, title="Solved Sudoku (revealing…)"),
                  console=console, refresh_per_second=30) as live:
            for r in range(9):
                temp[r] = board[r][:]
                live.update(render_board(temp, title="Solved Sudoku (revealing…)"))
                time.sleep(pause)
        console.print(render_board(board, title="Solved Sudoku"))
    else:
        temp = [[0]*9 for _ in range(9)]
        for r in range(9):
            temp[r] = board[r][:]
            print(render_board(temp, title="Solved Sudoku (revealing…)"))
            time.sleep(pause)
        print(render_board(board, title="Solved Sudoku"))

# ======================= Victory party (emoji flood + music) =======================

def victory_party_dance(skip: bool = False) -> None:
    if skip:
        return

    # Start music in background (plays once; keep your mp3 ~ DANCE_SECONDS)
    if playsound and os.path.exists(PARTY_MUSIC_FILE):
        threading.Thread(target=play_party_music, daemon=True).start()

    balloons  = ["🎈"] * 3 + ["🎉", "🎊", "✨"] + ["🎈"] * 3 + ["🎉", "🎊", "✨"]
    champagne = ["🍾", "🥂"] * 3
    streamers = ["✨", "💫", "⭐"] * 2
    base_tokens = balloons + champagne + streamers
    row = deque(base_tokens)

    def line_from_row():
        return " ".join(list(row))

    if RICH:
        console.print(Panel.fit("🍾🎉  LET’S CELEBRATE!  🎉🍾",
                                title="VICTORY!", border_style="bright_green"))
        total_frames = max(1, int(DANCE_SECONDS * DANCE_FPS))
        t0 = time.time()

        def frame(i: int):
            lines = []
            for k in range(6):
                row.rotate(1 + k)
                lines.append(line_from_row())
            # center pulse line
            pulse = " ".join(["🎈", "🍾", "🎊", "🥂", "✨", "🎉", "🥂", "🍾", "🎈"])
            center = f"[bold magenta]{pulse}[/bold magenta]" if i % 2 == 0 else f"[bold yellow]{pulse}[/bold yellow]"
            art = "\n".join(lines[:3] + [center] + lines[3:])
            border = "cyan" if (i // 2) % 2 == 0 else "magenta"
            return Panel(Align.center(art, vertical="middle"),
                         border_style=border, width=PARTY_WIDTH)

        with Live(frame(0), console=console, refresh_per_second=DANCE_FPS) as live:
            for i in range(1, total_frames + 1):
                live.update(frame(i))
                target = t0 + i / max(1, DANCE_FPS)
                sleep_left = target - time.time()
                if sleep_left > 0:
                    time.sleep(sleep_left)

        # EMOJI FLOOD FINALE 🌊🎉
        finale = " ".join(["🎈"] * 24 + ["🍾", "🥂"] * 12 + ["🎉", "🎊", "✨"] * 8)
        console.print(Panel.fit(finale, border_style="green", title="CHEERS!"))
    else:
        print("\nVICTORY! CHEERS! 🎉🍾")
        # simple text-mode splash
        print(("🎈🍾🎊✨ " * 12).strip())

# ======================= Main =======================

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Sudoku (API + MRV Solver) with max drama & music.")
    parser.add_argument("-d", "--difficulty", choices=["easy", "medium", "hard"], default=None,
                        help="Puzzle difficulty (no default; you will be prompted).")
    parser.add_argument("--api-url", default=os.environ.get("SUDOKU_API_URL", DEFAULT_API_URL),
                        help=f"API endpoint (default: {DEFAULT_API_URL})")
    parser.add_argument("--peek-seconds", type=float, default=DEFAULT_PEEK_SECONDS,
                        help="Visible fast 'peek' animation duration (Rich only).")
    parser.add_argument("--no-countdown", action="store_true", help="Skip the big 5..1 intro.")
    parser.add_argument("--no-party", action="store_true", help="Skip celebration animation & music.")
    parser.add_argument("--instant", action="store_true", help="Headless-fast mode (no animations).")
    parser.add_argument("--offline", action="store_true", help="Use built-in puzzle/solution; no network.")
    args = parser.parse_args(argv)

    try:
        difficulty = args.difficulty or ask_for_difficulty()

        if not args.instant:
            loading_dots("Fetching puzzle" if not args.offline else "Loading offline puzzle", seconds=1.2)

        board, api_solution, meta_diff = get_puzzle_and_solution(args.api_url, difficulty, force_offline=args.offline)

        # Show puzzle (unsolved) and hold for 3 seconds for dramatic tension
        title = f"Puzzle (difficulty: {meta_diff})"
        if RICH:
            console.print(render_board(board, title=title))
        else:
            print(render_board(board, title=title))
        if not args.instant:
            time.sleep(3.0)

        # Big 5→1 countdown
        countdown(skip=(args.no_countdown or args.instant))

        # Solve (with quick peek window)
        board_copy = [row[:] for row in board]
        t0 = time.time()
        ok = solve_with_mrv(board_copy,
                            peek_seconds=(0.0 if args.instant else max(0.0, args.peek_seconds)),
                            instant=args.instant)
        elapsed = time.time() - t0

        if ok:
            # Cheers sound (Windows multi-tone; BEL elsewhere)
            try:
                if WINSOUND:
                    beep(880, 200)   # A5
                    beep(988, 200)   # B5
                    beep(1047, 400)  # C6
                else:
                    print("\a", end="", flush=True)  # may beep in some terminals
            except Exception:
                pass

            msg = f"Solved in {elapsed:.2f}s"
            if RICH:
                console.print(Panel.fit(msg, border_style="bright_green"))
            else:
                print("\n" + msg)

            curtain_reveal(board_copy, pause=0.0 if args.instant else CURTAIN_PAUSE)
            victory_party_dance(skip=(args.no_party or args.instant))

            # Compare to provided solution (if any)
            if api_solution is not None:
                match = (board_copy == api_solution)
                if RICH:
                    console.print(f"\nMatches provided solution? [bold]{'✅ Yes' if match else '❌ No'}[/bold]")
                else:
                    print("\nMatches provided solution?", match)
            return 0
        else:
            if RICH:
                console.print("[red]No solution found (unexpected for this source).[/red]")
            else:
                print("No solution found (unexpected for this source).")
            return 2

    except KeyboardInterrupt:
        print("\nAborted by user.")
        return 130
    except Exception as e:
        if RICH:
            console.print(f"[red]Fatal error:[/red] {e}")
        else:
            print(f"Fatal error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
