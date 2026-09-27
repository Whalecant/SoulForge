# Soul Forge

A 2D stealth-platformer built in Python with Pygame. You play as Marquette Verne, the 73rd Soul Forge, navigating a large multi-room level, avoiding patrolling enemies, hacking terminals to open doors, collecting lore, and eventually confronting a boss — the Warden — whose defeat leads to one of two endings.

## Requirements

- Python 3
- Pygame
- NumPy

Install dependencies:
```
pip install pygame numpy
```

## Running from source

```
python main.py
```

The game window is 1000×750, targeting 60 FPS.

## Controls

| Action | Key |
|---|---|
| Move | Arrow keys / A, D |
| Jump | Space / W / Up |
| Fast fall | S / Down |
| Hack terminal | E |
| Pause | Esc |

## Project structure

| File | Responsibility |
|---|---|
| `main.py` | Entry point. Owns the game loop, the state machine, UI/menu rendering, and wiring between all other systems. |
| `player.py` | Player physics: movement, gravity, jumping, coyote time, wall slide/jump, mantling, animation. |
| `enemy.py` | Patrol-guard AI: patrol / chase / return states, line-of-sight detection, BFS waypoint pathfinding. |
| `warden.py` | Boss character: dialogue system, A* pathfinding/chase logic, defeat pose, sprite rendering. |
| `buildLevel.py` | Level data — rooms, platform geometry, terminal/door/enemy/lore-key placement — and the `build_level()` factory. |
| `hackTerminal.py` | Terminal object: hacking state, countdown timer, alarm behavior, sprite-based visual states, save/load. |
| `hackMinigame.py` | The hacking mini-game: a grid puzzle (find the key, avoid dummy tiles, reach the exit). |
| `door.py` | Doors that open once their required terminal(s) are hacked, with a delay and smooth slide animation. |
| `camera.py` | Room-snapping camera with a smooth lerp transition between rooms. |
| `checkpointManager.py` | Checkpoint zones that trigger autosave on entry. |
| `lore.py` | Journal/lore system: collectible `LoreKey` objects, `JournalManager`, and chapter text. |
| `saveManager.py` | Persistent save data (3 slots) as JSON, plus the shared `Button` UI class. |
| `audioManager.py` | SFX and music playback, including a custom pitch/speed-shift effect on the background music during alarms. |
| `spriteSheet.py` | Sprite-sheet slicer and frame-based `animation` helper. |
| `assets/` | Sprites (`assets/sprites/`) and music (`assets/music/bgm/`, `assets/music/sfx/`). |

## Game states

The game is driven by a single global `current_state` variable in `main.py`:

`MENU`, `LEVEL_SELECT`, `PLAYING`, `PAUSED`, `HACKING`, `GAME_OVER`, `JOURNAL`, `READING`, `WARDEN_DIALOGUE`, `WARDEN_INTRO`, `WARDEN_OUTRO`, `ENDING_CHOICE`, `ENDING_FADE`, `ENDING_EPILOGUE`, `ENDING`

Notable behavior:
- `hackReturnState` tracks which state to return to after `HACKING`, since it can be entered from either `PLAYING` or `ENDING_CHOICE`.
- The two ending terminals are identified by `t.room` (`"endingChoiceWarden"` / `"endingChoiceBreak"`), not by list position.
- `world_timer` does not tick during `ENDING_CHOICE`, `WARDEN_INTRO`, or `WARDEN_OUTRO`.

## Saving

Save data is stored per-OS, per-user — not next to the game files:

- Windows: `%APPDATA%\StealthPlatformer\save_data.json`
- macOS: `~/Library/Application Support/StealthPlatformer/save_data.json`
- Linux: `~/.local/share/StealthPlatformer/save_data.json`

Progress autosaves at checkpoints. There is no manual save.

## Adding new assets

Any code that loads an image or sound must resolve its path through the `resourcePath()` helper (already used in `spriteSheet.py`, `warden.py`, and `audioManager.py`):

```python
def resourcePath(relativePath):
    basePath = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(basePath, relativePath)
```

A plain relative path (e.g. `"assets/sprites/foo.png"`) works fine when running from source, but silently fails once bundled into an `.exe`. Any new `pygame.image.load(...)` or `pygame.mixer.Sound(...)` call needs this wrapper.

## Building a standalone `.exe`

Packaging uses PyInstaller with a checked-in `main.spec`:

```
pyinstaller main.spec --distpath "output/dist" --workpath "output/build" --noconfirm --clean
```

- `--noconfirm` skips the interactive overwrite prompt (important for non-interactive/`.bat` runs).
- `--clean` avoids reusing a stale cached build.

The finished executable is written to `output/dist/main.exe`.

**Testing a fresh build:** copy `main.exe` out of `output/dist/` to an unrelated folder before testing — running it from inside the project folder can hide bugs where the game still depends on loose files next to the source instead of the properly bundled/redirected versions.

## Known issues

- Enemy AI can occasionally get stuck on ledges — unresolved.
- `NotificationManager` (in `lore.py`) exists but isn't currently wired up anywhere in `main.py`.

## AI usage disclosure

Some code in this project — notably parts of the enemy AI — was generated with AI assistance. AI usage was otherwise kept to a minimum.
