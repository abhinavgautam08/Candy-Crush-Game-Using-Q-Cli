# Candy Crush Style Game

A modern Candy Crush-style match-3 game built with Python and Pygame.

## Features

- 8x8 grid of colorful candies
- Candy swapping mechanics
- Match detection for 3 or more candies
- Score tracking system
- Move limit with game over condition
- Smooth animations for swapping and matching
- Sound effects for game actions
- Modern UI with dark theme and rounded buttons

## Requirements

- Python 3.6+
- Pygame

## Installation

1. Create a virtual environment (recommended):
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install Pygame:
   ```
   pip install pygame
   ```

3. Run the game:
   ```
   python candy_crush.py
   ```

## Game Controls

- Click on a candy to select it
- Click on an adjacent candy to swap them
- Match 3 or more candies of the same color to score points
- Try to get the highest score before running out of moves

## Assets

The game looks for assets in the following directories:
- `assets/fonts/` - Font files (Roboto recommended)
- `assets/sounds/` - Sound effect files

## Customization

You can customize the game by modifying the constants at the top of the `candy_crush.py` file:
- Change colors
- Adjust grid size
- Modify scoring system
- Change the number of moves

## License

This project is open source and available for personal and educational use.
