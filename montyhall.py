import random
import argparse
import asyncio
from typing import Optional

# Textual imports
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Center
from textual.widgets import (
    Header, Footer, Button, Static, Input, Label, 
    ProgressBar, DataTable, Tabs, TabPane, Pretty,
    Collapsible, Rule
)
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.reactive import reactive, var
from textual import events


class SimulationResults:
    """Store and manage simulation results"""
    def __init__(self, num_games: int, num_doors: int):
        self.num_games = num_games
        self.num_doors = num_doors
        self.switch_wins = 0
        self.stay_wins = 0
        self.car_door_counts = {i: 0 for i in range(num_doors)}
        self.player_choice_counts = {i: 0 for i in range(num_doors)}
        
    @property
    def switch_rate(self) -> float:
        return self.switch_wins / self.num_games if self.num_games > 0 else 0
        
    @property
    def stay_rate(self) -> float:
        return self.stay_wins / self.num_games if self.num_games > 0 else 0
        
    @property
    def theoretical_switch_rate(self) -> float:
        return (self.num_doors - 1) / self.num_doors
        
    @property
    def theoretical_stay_rate(self) -> float:
        return 1 / self.num_doors


class GameState:
    """Manage the state of an interactive game"""
    def __init__(self, num_doors: int):
        self.num_doors = num_doors
        self.car_door = random.randint(0, num_doors - 1)
        self.player_choice: Optional[int] = None
        self.doors_opened = set()
        self.final_choice: Optional[int] = None
        self.game_over = False
        
    def make_initial_choice(self, door: int) -> bool:
        if 0 <= door < self.num_doors and self.player_choice is None:
            self.player_choice = door
            return True
        return False
    
    def open_doors_by_monty(self):
        """Monty opens all doors except car door and one other"""
        if self.player_choice is None:
            return
            
        doors_to_keep_closed = {self.car_door}
        if self.player_choice != self.car_door:
            doors_to_keep_closed.add(self.player_choice)
        else:
            # If player chose car door, keep one random other door closed
            other_doors = [i for i in range(self.num_doors) if i != self.car_door]
            doors_to_keep_closed.add(random.choice(other_doors))
        
        for door in range(self.num_doors):
            if door not in doors_to_keep_closed:
                self.doors_opened.add(door)
    
    def get_available_doors(self) -> list[int]:
        """Get doors that are still available to choose"""
        return [i for i in range(self.num_doors) if i not in self.doors_opened]
    
    def make_final_choice(self, door: int) -> bool:
        if door in self.get_available_doors():
            self.final_choice = door
            self.game_over = True
            return True
        return False
    
    def did_player_win(self) -> bool:
        return self.final_choice == self.car_door if self.final_choice is not None else False


class SimulationScreen(Screen):
    """Screen for running statistical simulations"""
    
    BINDINGS = [
        Binding("escape", "back", "Back to Menu")
    ]
    
    def __init__(self, num_games: int = 10000, num_doors: int = 3):
        super().__init__()
        self.num_games = num_games
        self.num_doors = num_doors
        self.results: Optional[SimulationResults] = None
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(f"[bold blue]Statistical Simulation[/] - {self.num_games:,} games with {self.num_doors} doors", 
                   classes="title"),
            Rule(),
            Static("Running simulation...", id="status"),
            ProgressBar(id="progress"),
            Container(id="results-container"),
            classes="simulation-screen"
        )
        yield Footer()
    
    async def on_mount(self) -> None:
        await self.run_simulation()
    
    async def run_simulation(self):
        """Run the simulation with progress updates"""
        self.results = SimulationResults(self.num_games, self.num_doors)
        progress = self.query_one("#progress", ProgressBar)
        status = self.query_one("#status", Static)
        
        # Run simulation in batches for progress updates
        batch_size = max(1, self.num_games // 100)
        completed = 0
        
        for batch_start in range(0, self.num_games, batch_size):
            batch_end = min(batch_start + batch_size, self.num_games)
            
            # Run batch
            for _ in range(batch_start, batch_end):
                # Generate game data
                car_door = random.randint(0, self.num_doors - 1)
                player_choice = random.randint(0, self.num_doors - 1)
                
                self.results.car_door_counts[car_door] += 1
                self.results.player_choice_counts[player_choice] += 1
                
                # Test switching strategy
                if self.simulate_game_outcome(True, car_door, player_choice):
                    self.results.switch_wins += 1
                    
                # Test staying strategy  
                if self.simulate_game_outcome(False, car_door, player_choice):
                    self.results.stay_wins += 1
                    
                completed += 1
            
            # Update progress
            progress.update(progress=completed / self.num_games * 100)
            status.update(f"Completed {completed:,} / {self.num_games:,} games...")
            await asyncio.sleep(0.01)  # Allow UI updates
        
        # Show results
        await self.show_results()
    
    def simulate_game_outcome(self, switch_strategy: bool, car_door: int, player_choice: int) -> bool:
        """Simulate a single game outcome"""
        # Determine which doors Monty opens
        doors_to_keep_closed = {car_door}
        if player_choice != car_door:
            doors_to_keep_closed.add(player_choice)
        else:
            other_doors = [i for i in range(self.num_doors) if i != car_door]
            doors_to_keep_closed.add(random.choice(other_doors))
        
        available_doors = [i for i in range(self.num_doors) 
                          if i in doors_to_keep_closed]
        
        if switch_strategy:
            # Switch to a different available door
            switch_options = [d for d in available_doors if d != player_choice]
            final_choice = random.choice(switch_options) if switch_options else player_choice
        else:
            # Stay with original choice
            final_choice = player_choice
            
        return final_choice == car_door
    
    async def show_results(self):
        """Display the simulation results"""
        if not self.results:
            return
            
        results_container = self.query_one("#results-container", Container)
        results_container.remove_children()
        
        # Main results
        switch_rate = self.results.switch_rate * 100
        stay_rate = self.results.stay_rate * 100
        theo_switch = self.results.theoretical_switch_rate * 100
        theo_stay = self.results.theoretical_stay_rate * 100
        
        await results_container.mount(
            Static("[bold green]SIMULATION COMPLETE![/]", classes="success"),
            Rule(),
            Static(f"[bold]Strategy Results:[/]"),
            Static(f"Switch: [green]{switch_rate:.1f}%[/] (theory: {theo_switch:.1f}%)"),
            Static(f"Stay:   [red]{stay_rate:.1f}%[/] (theory: {theo_stay:.1f}%)"),
            Static(f"Switch advantage: [bold]{switch_rate/stay_rate:.1f}x[/]"),
            Rule(),
            Collapsible(
                self.create_detailed_stats(),
                title="Detailed Statistics",
                collapsed=False
            )
        )
        
        self.query_one("#status", Static).update("[bold green]Simulation complete![/] Press ESC to return to menu.")
    
    def create_detailed_stats(self) -> Container:
        """Create detailed statistics display"""
        if not self.results:
            return Container()
            
        # Create data table for door distributions
        table = DataTable()
        table.add_column("Door", width=8)
        table.add_column("Car Location", width=15)
        table.add_column("Player Choice", width=15)
        table.add_column("Expected %", width=12)
        
        expected_pct = 100 / self.num_doors
        for door in range(self.num_doors):
            car_pct = (self.results.car_door_counts[door] / self.results.num_games) * 100
            choice_pct = (self.results.player_choice_counts[door] / self.results.num_games) * 100
            
            table.add_row(
                str(door),
                f"{car_pct:.1f}%",
                f"{choice_pct:.1f}%", 
                f"{expected_pct:.1f}%"
            )
        
        return Container(
            Static("[bold]Door Distribution Analysis:[/]"),
            table,
            classes="stats-container"
        )
    
    def action_back(self) -> None:
        self.app.pop_screen()


class InteractiveGameScreen(Screen):
    """Screen for playing the interactive game"""
    
    BINDINGS = [
        Binding("escape", "back", "Back to Menu")
    ]
    
    def __init__(self, num_doors: int = 3):
        super().__init__()
        self.num_doors = num_doors
        self.game_state: Optional[GameState] = None
        
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(f"[bold blue]Interactive Game[/] - {self.num_doors} doors", classes="title"),
            Rule(),
            Container(id="game-container"),
            classes="game-screen"
        )
        yield Footer()
    
    async def on_mount(self) -> None:
        await self.start_new_game()
    
    async def start_new_game(self):
        """Start a new game"""
        self.game_state = GameState(self.num_doors)
        await self.show_door_selection()
    
    async def show_door_selection(self):
        """Show initial door selection"""
        game_container = self.query_one("#game-container", Container)
        game_container.remove_children()
        
        # Create door buttons
        door_buttons = []
        for i in range(self.num_doors):
            door_buttons.append(Button(f"Door {i}", id=f"door-{i}", classes="door-button"))
        doors_container = Horizontal(*door_buttons, classes="doors-container")

        
        await game_container.mount(
            Static("[bold]Choose your initial door:[/]"),
            doors_container,
            Static("🚗 One door has a car, the others have goats! 🐐")
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if not self.game_state:
            self.notify("No game state!", severity="error")
            return
            
        button_id = event.button.id or ""
        
        # Debug notification to see what's happening
        self.notify(f"Button clicked: {button_id}")
        
        if button_id.startswith("door-"):
            door_num = int(button_id.split("-")[1])
            
            if self.game_state.player_choice is None:
                # Initial door selection
                self.notify(f"Making initial choice: Door {door_num}")
                if self.game_state.make_initial_choice(door_num):
                    self.notify(f"Choice made! Car is at door {self.game_state.car_door}")
                    self.show_monty_opens_doors()
                else:
                    self.notify("Failed to make initial choice", severity="error")
            elif not self.game_state.game_over:
                # Final choice
                self.notify(f"Making final choice: Door {door_num}")
                if self.game_state.make_final_choice(door_num):
                    self.show_game_result()
                else:
                    self.notify("Failed to make final choice", severity="error")
        
        elif button_id == "new-game":
            self.notify("Starting new game")
            self.start_new_game()
        elif button_id == "stay":
            if self.game_state.player_choice is not None and not self.game_state.game_over:
                self.notify(f"Staying with door {self.game_state.player_choice}")
                if self.game_state.make_final_choice(self.game_state.player_choice):
                    self.show_game_result()
                else:
                    self.notify("Failed to stay with choice", severity="error")
    
    async def show_monty_opens_doors(self):
        """Show Monty opening doors"""
        if not self.game_state:
            return
            
        self.game_state.open_doors_by_monty()
        game_container = self.query_one("#game-container", Container)
        game_container.remove_children()
        
        # Show door states
        doors_display = ""
        for i in range(self.num_doors):
            if i == self.game_state.player_choice:
                doors_display += f"[bold green]Door {i}: YOUR CHOICE[/]  "
            elif i in self.game_state.doors_opened:
                doors_display += f"[red]Door {i}: 🐐 GOAT[/]  "
            else:
                doors_display += f"[yellow]Door {i}: ? UNKNOWN[/]  "
        
        available_doors = self.game_state.get_available_doors()
        switch_options = [d for d in available_doors if d != self.game_state.player_choice]
        
        buttons_container = Horizontal(classes="choice-buttons")
        
        # Add stay button
        buttons_container.mount(
            Button(f"Stay with Door {self.game_state.player_choice}", 
                  id="stay", classes="choice-button stay-button")
        )
        
        # Add switch buttons
        for door in switch_options:
            buttons_container.mount(
                Button(f"Switch to Door {door}", 
                      id=f"door-{door}", classes="choice-button switch-button")
            )
        
        prob_stay = (1 / self.num_doors) * 100
        prob_switch = ((self.num_doors - 1) / self.num_doors) * 100
        
        await game_container.mount(
            Static(f"[bold]You chose Door {self.game_state.player_choice}[/]"),
            Static(doors_display),
            Rule(),
            Static("[bold]Monty revealed the goats! Now choose:[/]"),
            buttons_container,
            Rule(),
            Static(f"💡 [dim]Probability hint: Stay = {prob_stay:.1f}%, Switch = {prob_switch:.1f}%[/]")
        )
    
    async def show_game_result(self):
        """Show the final game result"""
        if not self.game_state:
            return
            
        game_container = self.query_one("#game-container", Container)
        game_container.remove_children()
        
        won = self.game_state.did_player_win()
        
        # Show all door contents
        doors_reveal = ""
        for i in range(self.num_doors):
            if i == self.game_state.car_door:
                doors_reveal += f"[bold green]Door {i}: 🚗 CAR[/]  "
            else:
                doors_reveal += f"[red]Door {i}: 🐐 GOAT[/]  "
        
        result_msg = ""
        if won:
            result_msg = "[bold green]🎉 CONGRATULATIONS! YOU WON THE CAR! 🎉[/]"
        else:
            result_msg = "[bold red]😔 Sorry, you got a goat. Better luck next time![/]"
        
        strategy = "SWITCHED" if self.game_state.final_choice != self.game_state.player_choice else "STAYED"
        
        await game_container.mount(
            Static(result_msg, classes="result-message"),
            Rule(),
            Static(doors_reveal),
            Rule(),
            Static(f"[bold]Your journey:[/]"),
            Static(f"• Initial choice: Door {self.game_state.player_choice}"),
            Static(f"• Final choice: Door {self.game_state.final_choice}"),
            Static(f"• Strategy: {strategy}"),
            Static(f"• Car was behind: Door {self.game_state.car_door}"),
            Rule(),
            Button("Play Again", id="new-game", classes="play-again-button")
        )
    
    def action_back(self) -> None:
        self.app.pop_screen()


class SettingsModal(ModalScreen[tuple[int, int]]):
    """Modal for simulation settings"""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("[bold]Simulation Settings[/]", classes="modal-title"),
            Rule(),
            Label("Number of doors (minimum 3):"),
            Input(value="3", id="doors-input"),
            Label("Number of games:"),
            Input(value="10000", id="games-input"),
            Rule(),
            Horizontal(
                Button("Start Simulation", variant="primary", id="start"),
                Button("Cancel", id="cancel"),
                classes="button-row"
            ),
            classes="settings-modal"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start":
            doors_input = self.query_one("#doors-input", Input)
            games_input = self.query_one("#games-input", Input) 
            
            try:
                doors = max(3, int(doors_input.value))
                games = max(1, int(games_input.value))
                self.dismiss((games, doors))
            except ValueError:
                # Invalid input, keep modal open
                doors_input.focus()
        elif event.button.id == "cancel":
            self.dismiss(None)


class GameSettingsModal(ModalScreen[int]):
    """Modal for interactive game settings"""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("[bold]Game Settings[/]", classes="modal-title"),
            Rule(),
            Label("Number of doors (minimum 3):"),
            Input(value="3", id="doors-input"),
            Rule(),
            Horizontal(
                Button("Start Game", variant="primary", id="start"),
                Button("Cancel", id="cancel"),
                classes="button-row"
            ),
            classes="settings-modal"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start":
            doors_input = self.query_one("#doors-input", Input)
            
            try:
                doors = max(3, int(doors_input.value))
                self.dismiss(doors)
            except ValueError:
                doors_input.focus()
        elif event.button.id == "cancel":
            self.dismiss(None)


class MontyHallApp(App):
    """Main Monty Hall TUI Application"""
    
    CSS = """
    .title {
        text-align: center;
        padding: 1;
    }
    
    .menu-container {
        align: center middle;
        max-width: 60;
    }
    
    .menu-button {
        width: 100%;
        margin: 1;
    }
    
    .doors-container {
        align: center middle;
        padding: 2;
    }
    
    .door-button {
        margin: 0 1;
        min-width: 12;
    }
    
    .choice-buttons {
        align: center middle;
        padding: 1;
    }
    
    .choice-button {
        margin: 0 1;
    }
    
    .stay-button {
        background: red 30%;
    }
    
    .switch-button {
        background: green 30%;
    }
    
    .play-again-button {
        dock: bottom;
        margin: 1;
        background: blue;
    }
    
    .result-message {
        text-align: center;
        padding: 1;
    }
    
    .settings-modal {
        align: center middle;
        background: $panel;
        border: thick $primary;
        width: 50;
        height: auto;
        padding: 1;
    }
    
    .modal-title {
        text-align: center;
        padding-bottom: 1;
    }
    
    .button-row {
        align: center middle;
        padding-top: 1;
    }
    
    .success {
        color: green;
        text-align: center;
    }
    
    .stats-container {
        padding: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit")
    ]
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("[bold blue]🎰 MONTY HALL PROBLEM SIMULATOR 🎰[/]", classes="title"),
            Static("[dim]The famous probability puzzle with a beautiful TUI![/]", classes="title"),
            Rule(),
            Container(
                Button("📊 Statistical Simulation", id="simulation", classes="menu-button"),
                Button("🎮 Interactive Game", id="game", classes="menu-button"), 
                Button("❓ About", id="about", classes="menu-button"),
                Button("🚪 Quit", id="quit", classes="menu-button"),
                classes="menu-container"
            ),
            classes="main-menu"
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        
        if button_id == "simulation":
            def check_simulation_result(result):
                if result:
                    games, doors = result
                    self.push_screen(SimulationScreen(games, doors))
            self.push_screen(SettingsModal(), check_simulation_result)
                
        elif button_id == "game":
            def check_game_result(doors):
                if doors:
                    self.push_screen(InteractiveGameScreen(doors))
            self.push_screen(GameSettingsModal(), check_game_result)
                
        elif button_id == "about":
            self.show_about()
            
        elif button_id == "quit":
            self.exit()
    
    def show_about(self):
        """Show about information"""
        about_text = """[bold blue]The Monty Hall Problem[/bold blue]

Named after game show host Monty Hall, this famous probability puzzle demonstrates counter-intuitive statistics.

[bold]The Setup:[/bold]
• You choose one of three doors (one has a car, others have goats)
• Monty opens a door with a goat (not your choice, not the car)
• You can switch to the remaining door or stay with your choice

[bold]The Surprise:[/bold]
• Staying gives you a 1/3 (33.3%) chance of winning
• Switching gives you a 2/3 (66.7%) chance of winning!

[bold]Why?[/bold]
Your initial choice had a 1/3 chance of being correct. When Monty eliminates a wrong door, the remaining door gets the combined probability of all the doors you didn't pick: 2/3!

With more doors, this effect becomes even more dramatic. With 100 doors, staying gives you 1% chance, while switching gives you 99% chance!

This simulator lets you run statistical simulations and play interactively to experience the puzzle firsthand.

Press ESC to return to the menu."""
        
        # Create a simple screen for about info
        class AboutScreen(Screen):
            BINDINGS = [Binding("escape", "back", "Back")]
            
            def compose(self):
                yield Header()
                yield Container(
                    Static(about_text, classes="about-text"),
                    classes="about-container"
                )
                yield Footer()
            
            def action_back(self):
                self.app.pop_screen()
        
        self.push_screen(AboutScreen())


def monty_hall_game_simple(switch_strategy: bool, num_doors: int = 3) -> bool:
    """Simple version for command line mode"""
    car_door = random.randint(0, num_doors - 1)
    player_choice = random.randint(0, num_doors - 1)
    
    # Monty's doors
    doors_to_keep_closed = {car_door}
    if player_choice != car_door:
        doors_to_keep_closed.add(player_choice)
    else:
        other_doors = [i for i in range(num_doors) if i != car_door]
        doors_to_keep_closed.add(random.choice(other_doors))
    
    available_doors = list(doors_to_keep_closed)
    
    if switch_strategy:
        switch_options = [d for d in available_doors if d != player_choice]
        final_choice = random.choice(switch_options) if switch_options else player_choice
    else:
        final_choice = player_choice
        
    return final_choice == car_door


def run_simple_simulation(num_games: int, num_doors: int, quiet: bool = False):
    """Simple command-line simulation"""
    switch_wins = sum(monty_hall_game_simple(True, num_doors) for _ in range(num_games))
    stay_wins = sum(monty_hall_game_simple(False, num_doors) for _ in range(num_games))
    
    switch_rate = switch_wins / num_games
    stay_rate = stay_wins / num_games
    theoretical_switch = (num_doors - 1) / num_doors
    theoretical_stay = 1 / num_doors
    
    if quiet:
        print(f"Doors: {num_doors}, Games: {num_games:,}")
        print(f"Switch: {switch_rate:.1%} (theory: {theoretical_switch:.1%})")
        print(f"Stay:   {stay_rate:.1%} (theory: {theoretical_stay:.1%})")
        print(f"Switch advantage: {switch_rate/stay_rate:.1f}x")
    else:
        print(f"\nMonty Hall Simulation Results:")
        print(f"{'='*50}")
        print(f"Games: {num_games:,} | Doors: {num_doors}")
        print(f"Switch Strategy: {switch_wins:,} wins ({switch_rate:.1%}) - Theory: {theoretical_switch:.1%}")
        print(f"Stay Strategy:   {stay_wins:,} wins ({stay_rate:.1%}) - Theory: {theoretical_stay:.1%}")
        print(f"Switch Advantage: {switch_rate/stay_rate:.1f}x better")


def main():
    """Main entry point with argparse support"""
    parser = argparse.ArgumentParser(
        description="Monty Hall Problem Simulator with beautiful TUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Launch interactive TUI (default)
  %(prog)s -s 10000 -d 3            # Quick command-line simulation
  %(prog)s -s 50000 -d 10 -q        # Quiet simulation for scripting
  %(prog)s --tui                    # Force TUI mode
        """
    )
    
    parser.add_argument(
        '-s', '--simulate',
        type=int,
        metavar='GAMES',
        help='Run command-line simulation with specified number of games'
    )
    
    parser.add_argument(
        '-d', '--doors',
        type=int,
        default=3,
        metavar='N',
        help='Number of doors (default: 3, minimum: 3)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet output for command-line simulation'
    )
    
    parser.add_argument(
        '--tui',
        action='store_true',
        help='Force TUI mode (default when no simulation specified)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Monty Hall Simulator v3.0 (with Textual TUI)'
    )
    
    args = parser.parse_args()
    
    # Validate doors
    if args.doors < 3:
        parser.error("Number of doors must be at least 3")
    
    # Determine mode
    if args.simulate is not None and not args.tui:
        # Command-line simulation mode
        if args.simulate <= 0:
            parser.error("Number of games must be positive")
        run_simple_simulation(args.simulate, args.doors, args.quiet)
    else:
        # TUI mode (default)
        try:
            app = MontyHallApp()
            app.run()
        except ImportError:
            print("Textual not installed. Install with: pip install textual")
            print("Running simple command-line simulation instead...")
            run_simple_simulation(args.simulate or 10000, args.doors, args.quiet)
        except Exception as e:
            print(f"TUI error: {e}")
            print("Falling back to command-line simulation...")
            run_simple_simulation(args.simulate or 10000, args.doors, args.quiet)


if __name__ == "__main__":
    main()