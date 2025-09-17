# Monty Hall Simulator

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)

A terminal-based simulator for the famous Monty Hall probability puzzle, featuring both interactive gameplay and statistical simulations. 

![Interactive Gameplay Screenshot](images/cute-goat-door.png)

## Features

- **Interactive TUI**: Play the Monty Hall game with an intuitive terminal interface
  - Visual representation of doors and game state
  - Real-time feedback and statistics
  - Customizable number of doors (3-100)

- **Statistical Simulation**: Run simulations to verify the probabilities for yourself
  - Compare "switch" vs. "stay" strategies
  - View theoretical vs. actual results
  - Export results for further analysis

- **Customizable Parameters**: Adjust the number of doors and simulation runs
  - Test with any number of doors (3 or more)
  - Run from 1 to 1,000,000 simulations
  - Configure output verbosity

- **Command-line Interface**: Quick simulations for scripting or analysis
  - Perfect for educational demonstrations
  - Easy integration with data analysis workflows
  - JSON output option for programmatic use

- **Educational Content**: Built-in explanation of the mathematics
  - Clear explanation of the Monty Hall paradox
  - Historical context of the problem
  - Interactive exploration of probability concepts

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for package management and virtual environments.

### Prerequisites

- Python 3.8 or higher
- Terminal with ANSI color support (most modern terminals)

### Standard Installation

1. Install uv (if you haven't already):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/matchagradient/monty-hall-sim.git
   cd monty-hall-sim
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   uv pip install -e .
   ```

### Alternative Installation with pip

If you prefer not to use uv:

```bash
git clone https://github.com/matchagradient/monty-hall-sim.git
cd monty-hall-sim
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Troubleshooting

If you encounter any issues during installation:

- Make sure you have Python 3.8+ installed
- Check that your terminal supports ANSI colors
- Ensure you have proper permissions to install packages
- Try creating the virtual environment in a different location if you see permission errors

## Usage

### Interactive TUI Mode

Launch the interactive terminal user interface:

```bash
uv run python montyhall.py
```

Or if your virtual environment is already activated:

```bash
python montyhall.py
```

#### TUI Navigation

In the TUI, you can:
- Use arrow keys or Tab to navigate between options
- Press Enter to select buttons or confirm choices
- Use Escape to go back or exit dialogs
- Press 'q' to quit the application

The TUI consists of several sections:
- **Main Menu**: Choose between playing a game, running simulations, or viewing information
- **Game Interface**: Select doors, make decisions, and see results
- **Simulation Settings**: Configure parameters for statistical simulations
- **Results View**: Examine detailed statistics and probability distributions
- **About Section**: Learn about the Monty Hall problem and this simulator

### Command-line Simulation

For quick simulations without the TUI, use the command-line options:

```bash
# Run a simulation of 10,000 games with 3 doors
python montyhall.py -s 10000 -d 3

# Run a simulation with 50,000 games and 10 doors, with quiet output
python montyhall.py -s 50000 -d 10 -q

# Output results in JSON format for scripting
python montyhall.py -s 1000 -d 5 --json

# Force TUI explicitly
python montyhall.py --tui

# See all available options
python montyhall.py --help
```

### Command-line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-s, --simulations` | Number of simulations to run | 1000 |
| `-d, --doors` | Number of doors in the game | 3 |
| `-q, --quiet` | Suppress output except for final results | False |
| `--json` | Output results in JSON format | False |
| `--tui` | Force launch in TUI mode | False |
| `-h, --help` | Show help message | - |

## Examples

### Example 1: Basic Simulation

```bash
$ python montyhall.py -s 10000 -d 3

Monty Hall Simulation Results:
==================================================
Games: 10,000 | Doors: 3
Switch Strategy: 6,689 wins (66.9%) - Theory: 66.7%
Stay Strategy:   3,311 wins (33.1%) - Theory: 33.3%
Switch Advantage: 2.0x better
```

### Example 2: More Doors

```bash
$ python montyhall.py -s 10000 -d 10

Monty Hall Simulation Results:
==================================================
Games: 10,000 | Doors: 10
Switch Strategy: 9,012 wins (90.1%) - Theory: 90.0%
Stay Strategy:   988 wins (9.9%) - Theory: 10.0%
Switch Advantage: 9.1x better
```

### Example 3: JSON Output for Scripting

```bash
$ python montyhall.py -s 1000 -d 5 --json
{
  "simulations": 1000,
  "doors": 5,
  "results": {
    "switch": {
      "wins": 803,
      "percentage": 80.3,
      "theoretical": 80.0
    },
    "stay": {
      "wins": 197,
      "percentage": 19.7,
      "theoretical": 20.0
    }
  },
  "advantage": 4.1
}
```

## The Monty Hall Problem

The Monty Hall problem is a famous probability puzzle based on the American game show "Let's Make a Deal". It demonstrates how counter-intuitive probability can be.

### The Setup

1. There are three doors: behind one door is a car; behind the others, goats.
2. You pick a door (say, No. 1).
3. The host, who knows what's behind the doors, opens another door (say, No. 3) which has a goat.
4. He then asks if you want to switch to door No. 2 or stick with your original choice.

### The Surprise

- If you stick with your original choice, you have a 1/3 chance of winning the car.
- If you switch, you have a 2/3 chance of winning the car!

### Mathematical Explanation

When you first choose a door, you have a 1/3 chance of picking the car and a 2/3 chance of picking a goat.

If you picked the car (1/3 chance), switching will lose.
If you picked a goat (2/3 chance), the host will reveal the other goat, and switching will win.

Thus, switching gives you a 2/3 probability of winning, while staying gives only 1/3.

### Generalization to N Doors

With more doors, the advantage of switching becomes even more dramatic. For n doors:

- Staying gives you a 1/n chance of winning.
- Switching gives you a (n-1)/n chance of winning!

For example, with 100 doors:
- Staying gives you a 1% chance of winning.
- Switching gives you a 99% chance of winning!

### Historical Context

The problem was named after Monty Hall, the host of the television game show "Let's Make a Deal." It gained fame when Marilyn vos Savant wrote about it in her "Ask Marilyn" column in Parade magazine in 1990. Her solution, which advocated for switching, sparked intense debate among mathematicians and the general public.

## Screenshots

### Main Menu
![Main Screen](images/montyhall-main-screen.png)

### Interactive Gameplay
![Interactive Gameplay](images/montyhall-interactive.png)

### Simulation Results
![Simulation View](images/montyhall-simulation.png)

## FAQ

### Why does switching give a higher probability of winning?

When you initially choose a door, you have a 1/n chance of being correct (where n is the number of doors). The host then reveals all but one of the remaining doors, all of which have goats. This concentrates the entire remaining probability (n-1)/n into the single unopened door that you didn't choose.

### Does this work with any number of doors?

Yes! The simulator allows you to test with any number of doors (3 or more). As the number of doors increases, the advantage of switching becomes more pronounced.

### Is this simulator accurate?

The simulator uses a proper implementation of the Monty Hall problem rules and has been tested against theoretical probabilities. The simulation results will converge to the theoretical values as the number of simulations increases.

## Performance

The simulator is optimized for performance:

- 10,000 simulations with 3 doors complete in approximately 0.2 seconds
- 100,000 simulations with 3 doors complete in approximately 2 seconds
- 1,000,000 simulations with 3 doors complete in approximately 20 seconds

Performance scales linearly with both the number of simulations and the number of doors.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the package in development mode:
   ```bash
   uv pip install -e ".[dev]"
   ```
4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Making Changes

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Make your changes
3. Run tests and linting:
   ```bash
   pytest
   ruff check .
   ruff format --check .
   ```
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the famous probability puzzle and the TV show "Let's Make a Deal"
- Built with [Textual](https://textual.textualize.io/) for the beautiful terminal interface
- Uses [uv](https://github.com/astral-sh/uv) for fast Python package management
- Mathematical explanation based on the work of Marilyn vos Savant and other statisticians

## See Also

- [The Monty Hall Problem on Wikipedia](https://en.wikipedia.org/wiki/Monty_Hall_problem)
- [Original "Ask Marilyn" column](https://web.archive.org/web/20130121183432/http://marilynvossavant.com/game-show-problem/)
- [Textual Documentation](https://textual.textualize.io/)
