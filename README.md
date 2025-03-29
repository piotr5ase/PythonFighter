# CrapFighter

CrapFighter is a 2D fighting game built using Python and Pygame. Players can select characters, choose maps, and engage in battles using various abilities and attacks.

## Features

- **Character Selection**: Choose from a variety of characters, each with unique stats and abilities.
- **Customizable Characters**: Characters are fully customizable, allowing players to modify stats, abilities, and animations via JSON files.
- **Map Selection**: Select different maps to fight on, each with unique backgrounds and layouts.
- **Abilities**: Use light/heavy punches, kicks, special abilities, and ultimate moves to defeat your opponent.
- **Blocking and Defense**: Tap to block attacks and reduce damage.
- **Ultimate Charge System**: Build up your ultimate charge by performing actions and landing hits.
- **Game Over Screen**: Displays the winner when one player's health reaches zero.

## Controls

### Player 1
- **Movement**: `A` (left), `D` (right)
- **Jump**: `W`
- **Block**: `S` (tap to block)
- **Abilities**:
  - `1`: Light Punch
  - `2`: Heavy Punch
  - `3`: Light Kick
  - `4`: Heavy Kick
  - `5`: V-Skill
  - `6`: V-Trigger
  - `7`: V-Reversal
  - `8`: EX-Buff

### Player 2
- **Movement**: Arrow keys (`←`, `→`)
- **Jump**: `↑`
- **Block**: `↓` (tap to block)
- **Abilities**:
  - `Numpad 1`: Light Punch
  - `Numpad 2`: Heavy Punch
  - `Numpad 3`: Light Kick
  - `Numpad 4`: Heavy Kick
  - `Numpad 5`: V-Skill
  - `Numpad 6`: V-Trigger
  - `Numpad 7`: V-Reversal
  - `Numpad 8`: EX-Buff

## How to Play

1. **Run the Game**: Start the game by running `main.py`.
2. **Select Characters**: Each player selects their character from the available options.
3. **Select Map**: Choose a map to fight on.
4. **Battle**: Use the controls to move, attack, and defend. The first player to reduce their opponent's health to zero wins.
5. **Game Over**: The winner is displayed, and the game ends.

## Requirements

- Python 3.x
- Pygame library (`pip install pygame`)

## Installation

1. Clone or download the repository.
2. Ensure Python 3.x is installed on your system.
3. Install Pygame by running:
   ```
   pip install pygame
   ```
4. Run the game:
   ```
   python main.py
   ```

## Assets

- **Characters**: Located in `assets/characters/`. Each character has unique animations and stats defined in `character.json`.
- **Maps**: Located in `assets/stages/`. Each map has unique background, foreground, and ground assets defined in `map.json`.

Enjoy the game!
