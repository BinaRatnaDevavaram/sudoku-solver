# 🎯 Sudoku Solver — With Drama, Flair & a Victory Party! 🎉

Welcome to the **most extra** Sudoku solver on GitHub — where solving a puzzle isn't just logic…  it's a **full-blown celebration**. 🥳

Forget boring CLI solvers. Here, you'll:

- Pick your puzzle difficulty.
- Watch a **huge cinematic countdown** (5️⃣ 4️⃣ 3️⃣ 2️⃣ 1️⃣).
- Witness your puzzle being solved in style.
- End with a **flood of balloons, champagne, and streamers** — plus disco music if you want! 🍾🎈🎉

---

## ✨ Features

- 🎮 **Difficulty selection**: Easy, Medium, Hard — fetched fresh from an online Sudoku API.
- 🕒 **3-second preview** of the unsolved board before countdown.
- ⏳ **Big, dramatic countdown**: 5️⃣ → 4️⃣ → 3️⃣ → 2️⃣ → 1️⃣.
- 🧠 **MRV Backtracking solver** — fast and reliable.
- 🎵 **Cheers sound effect** when solved (Windows + terminal bell fallback).
- 💃 **Victory party mode** — emoji flood & optional disco music with `party.mp3`.
- 🎨 **Rich** integration for colorful boards, panels, and animations.
- 🛡 Works even without Rich or sound libraries — still solves puzzles in plain mode.

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/sudoku-solver-party.git
cd sudoku-solver-party
pip install -r requirements.txt
```

## 🎵 Party Music Setup

- If you want the disco celebration to really kick:
- Place a party.mp3 in the same folder as sudoku_solver.py.
- Make it roughly 5 seconds long (to match the celebration length).
- Royalty-free options: Pixabay Music or Free Music Archive.
- If no party.mp3 is present, emojis still go wild — just in silence.

🚀 Usage

python sudoku_solver.py

You’ll be prompted to choose:

easy | medium | hard

Then:

The puzzle appears (3-second preview).

Big countdown starts.

Solver does its magic.

Celebration erupts 🥳.

## 🖼 Example Output

Puzzle Preview

. . 3 | . 2 . | 6 . .
9 . . | 3 . 5 | . . 1
. . 1 | 8 . 6 | 4 . .
------+-------+------
. . 8 | 1 . 2 | 9 . .
7 . . | . . . | . . 8
. . 6 | 7 . 8 | 2 . .
------+-------+------
. . 2 | 6 . 9 | 5 . .
8 . . | 2 . 3 | . . 9
. . 5 | . 1 . | 3 . .

Countdown Mode

5️⃣
4️⃣
3️⃣
2️⃣
1️⃣

Victory Mode

🎈🍾🎉🎈🍾🎉🎈🍾🎉
🎉🍾🎈🎉🍾🎈🎉🍾🎈
... (party continues)

## 🔧 Requirements

See requirements.txt for dependencies.

requests — required (API fetch)

rich — optional but recommended (pretty UI)

playsound — optional (party music)

## 💡 Tips

Want a longer party? Increase DANCE_SECONDS in the script and match your party.mp3 length.

Don’t have Rich installed? No worries — the script falls back to plain text mode.

Works on macOS / Linux / Windows (sound is best on Windows via winsound).

## 🏆 Credits

Sudoku API — youdosudoku.com

Rich — <https://github.com/Textualize/rich>

Music — Your choice of royalty-free celebration track

## 📜 License

MIT — Go wild, fork it, remix it, and celebrate your own victories.

## 📂 Project Structure

/4.sudokusolver
├── sudoku_solver.py
├── requirements.txt
├── README.md
└── party.mp3   # optional
