import tkinter as tk
from tkinter import ttk, messagebox
import copy
import math

class AdvancedTicTacToe:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Tic Tac Toe")
        self.root.geometry("900x650")
        
        # Game state
        self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        self.current_player = 'X'  # X = User, O = Bot
        self.user_score = 0
        self.bot_score = 0
        self.user_spears = 0
        self.bot_spears = 0
        self.game_started = False
        self.game_over = False
        
        # Turn system
        self.turn_ratio = [1, 1]  # [user_moves, bot_moves]
        self.current_turn_count = 0
        self.is_user_turn_phase = True
        self.starting_player = 'user'
        
        # Point values for each position
        self.point_values = [
            [80, 80, 80],  # Top row
            [40, 40, 40],  # Middle row  
            [30, 30, 30]   # Bottom row
        ]
        
        # Spear mode
        self.spear_mode = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with left and right panels
        main_container = tk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel for game
        left_panel = tk.Frame(main_container)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel for log
        right_panel = tk.Frame(main_container, width=300)
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        
        # Configuration frame (left panel)
        config_frame = ttk.LabelFrame(left_panel, text="Game Configuration", padding=10)
        config_frame.pack(pady=10, fill='x')
        
        # Turn ratio setting
        ttk.Label(config_frame, text="Turn Ratio (User:Bot):").grid(row=0, column=0, sticky='w')
        self.turn_ratio_var = tk.StringVar(value="1:1")
        turn_combo = ttk.Combobox(config_frame, textvariable=self.turn_ratio_var, 
                                values=["1:1", "1:2", "2:1"], state="readonly", width=10)
        turn_combo.grid(row=0, column=1, padx=5)
        
        # Starting player
        ttk.Label(config_frame, text="Starting Player:").grid(row=0, column=2, padx=(20,0), sticky='w')
        self.starting_player_var = tk.StringVar(value="user")
        start_combo = ttk.Combobox(config_frame, textvariable=self.starting_player_var,
                                 values=["user", "bot"], state="readonly", width=10)
        start_combo.grid(row=0, column=3, padx=5)
        
        # Spear settings
        ttk.Label(config_frame, text="User Spears:").grid(row=1, column=0, sticky='w', pady=(5,0))
        self.user_spears_var = tk.IntVar(value=1)
        user_spear_spin = ttk.Spinbox(config_frame, from_=0, to=5, textvariable=self.user_spears_var, width=10)
        user_spear_spin.grid(row=1, column=1, padx=5, pady=(5,0))
        
        ttk.Label(config_frame, text="Bot Spears:").grid(row=1, column=2, padx=(20,0), sticky='w', pady=(5,0))
        self.bot_spears_var = tk.IntVar(value=1)
        bot_spear_spin = ttk.Spinbox(config_frame, from_=0, to=5, textvariable=self.bot_spears_var, width=10)
        bot_spear_spin.grid(row=1, column=3, padx=5, pady=(5,0))
        
        # Start and Reset buttons
        button_frame = tk.Frame(config_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="START GAME", command=self.start_game)
        self.start_button.pack(side='left', padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="RESET GAME", command=self.reset_game)
        self.reset_button.pack(side='left', padx=5)
        
        # Game info frame (left panel)
        info_frame = ttk.LabelFrame(left_panel, text="Game Status", padding=10)
        info_frame.pack(pady=10, fill='x')
        
        # Score display
        self.user_score_label = ttk.Label(info_frame, text="User Score: 0", font=('Arial', 12, 'bold'))
        self.user_score_label.grid(row=0, column=0, padx=10)
        
        self.bot_score_label = ttk.Label(info_frame, text="Bot Score: 0", font=('Arial', 12, 'bold'))
        self.bot_score_label.grid(row=0, column=1, padx=10)
        
        # Spear display
        self.user_spears_label = ttk.Label(info_frame, text="User Spears: 0", font=('Arial', 10))
        self.user_spears_label.grid(row=1, column=0, padx=10)
        
        self.bot_spears_label = ttk.Label(info_frame, text="Bot Spears: 0", font=('Arial', 10))
        self.bot_spears_label.grid(row=1, column=1, padx=10)
        
        # Turn display
        self.turn_label = ttk.Label(info_frame, text="Game not started", font=('Arial', 11))
        self.turn_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Spear mode button
        self.spear_button = ttk.Button(info_frame, text="Use Spear", command=self.toggle_spear_mode, state='disabled')
        self.spear_button.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Game board frame (left panel)
        board_frame = ttk.LabelFrame(left_panel, text="Game Board", padding=10)
        board_frame.pack(pady=10)
        
        # Create game board
        self.buttons = []
        for row in range(3):
            button_row = []
            for col in range(3):
                btn = tk.Button(board_frame, text='', font=('Arial', 20, 'bold'), 
                              width=4, height=2, command=lambda r=row, c=col: self.make_move(r, c),
                              state='disabled')
                btn.grid(row=row, column=col, padx=2, pady=2)
                
                # Add point value labels
                point_label = tk.Label(board_frame, text=f"{self.point_values[row][col]}pts", 
                                     font=('Arial', 8), fg='gray')
                point_label.grid(row=row+3, column=col)
                
                button_row.append(btn)
            self.buttons.append(button_row)
        
        # Log panel (right panel)
        log_frame = ttk.LabelFrame(right_panel, text="Move Log", padding=10)
        log_frame.pack(fill='both', expand=True)
        
        # Log text widget with scrollbar
        log_container = tk.Frame(log_frame)
        log_container.pack(fill='both', expand=True)
        
        self.log_text = tk.Text(log_container, wrap=tk.WORD, height=20, width=30, 
                               font=('Arial', 9), state='disabled')
        log_scrollbar = ttk.Scrollbar(log_container, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        # Log legend
        legend_frame = tk.Frame(log_frame)
        legend_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(legend_frame, text="Row Requirements:", font=('Arial', 9, 'bold')).pack()
        tk.Label(legend_frame, text="Top Row: R1 + R2", font=('Arial', 8), fg='blue').pack()
        tk.Label(legend_frame, text="Middle Row: R2 only", font=('Arial', 8), fg='green').pack()
        tk.Label(legend_frame, text="Bottom Row: R1 only", font=('Arial', 8), fg='red').pack()
        
    def start_game(self):
        # Parse turn ratio
        ratio = self.turn_ratio_var.get().split(':')
        self.turn_ratio = [int(ratio[0]), int(ratio[1])]
        
        # Set starting player
        self.starting_player = self.starting_player_var.get()
        self.current_player = 'X' if self.starting_player == 'user' else 'O'
        self.is_user_turn_phase = (self.starting_player == 'user')
        
        # Set spears
        self.user_spears = self.user_spears_var.get()
        self.bot_spears = self.bot_spears_var.get()
        
        # Enable game
        self.game_started = True
        self.game_over = False
        self.current_turn_count = 0
        
        # Enable buttons
        for row in self.buttons:
            for btn in row:
                btn.config(state='normal', bg='lightgray')
        
        self.start_button.config(state='disabled')
        self.reset_button.config(state='normal')
        self.spear_button.config(state='normal')
        
        # Log game start
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"🎮 GAME STARTED - {self.starting_player.upper()} goes first!\n")
        self.log_text.insert(tk.END, f"Turn Ratio: {self.turn_ratio[0]}:{self.turn_ratio[1]} (User:Bot)\n")
        self.log_text.insert(tk.END, f"Spears: User={self.user_spears}, Bot={self.bot_spears}\n")
        self.log_text.insert(tk.END, "=" * 30 + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
        self.update_display()
        
        # FIX: If bot starts first, trigger bot move
        if self.starting_player == 'bot':
            self.root.after(500, self.bot_move)
    
    def log_move(self, row, col, player):
        """Log a move with the required row combination"""
        # Determine row requirement based on row
        if row == 0:  # Top row
            row_req = "R1 + R2"
        elif row == 1:  # Middle row
            row_req = "R2"
        else:  # Bottom row (row == 2)
            row_req = "R1"
        
        # Create log entry
        log_entry = f"{player}: {row_req} on {row},{col}\n"
        
        # Add to log
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # Auto-scroll to bottom
        self.log_text.config(state='disabled')
    
    def log_spear_attack(self, row, col, player):
        """Log a spear attack"""
        log_entry = f"{player}: ⚔️ SPEAR ATTACK on {row},{col}\n"
        
        # Add to log
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # Auto-scroll to bottom
        self.log_text.config(state='disabled')
    
    def log_game_result(self, winner, win_type=""):
        """Log the final game result"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, "\n" + "=" * 20 + "\n")
        
        if winner == "tie":
            self.log_text.insert(tk.END, "TIE GAME\n")
        else:
            win_text = f"{winner} WIN"
            if win_type:
                win_text += f" ({win_type})"
            self.log_text.insert(tk.END, win_text + "\n")
        
        self.log_text.insert(tk.END, f"User : {self.user_score}\n")
        self.log_text.insert(tk.END, f"Bot : {self.bot_score}\n")
        self.log_text.insert(tk.END, "=" * 20 + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def make_move(self, row, col):
        if not self.game_started or self.game_over:
            return
            
        if self.spear_mode:
            self.use_spear(row, col)
            return
        
        # Check if it's the right player's turn
        if (self.is_user_turn_phase and self.current_player != 'X') or \
           (not self.is_user_turn_phase and self.current_player != 'O'):
            return
            
        if self.board[row][col] != '':
            return
        
        # Make the move
        self.board[row][col] = self.current_player
        self.buttons[row][col].config(text=self.current_player, 
                                    bg='lightblue' if self.current_player == 'X' else 'lightcoral')
        
        # Update score
        if self.current_player == 'X':
            self.user_score += self.point_values[row][col]
        else:
            self.bot_score += self.point_values[row][col]
        
        # Log the move
        self.log_move(row, col, 'User' if self.current_player == 'X' else 'Bot')
        
        # Check for absolute win
        winner = self.check_absolute_win()
        if winner:
            self.game_over = True
            winner_name = 'User' if winner == 'X' else 'Bot'
            self.update_display()  # Update display before logging/showing result
            self.log_game_result(winner_name, "ABSOLUTE WIN")
            messagebox.showinfo("Game Over", f"{winner_name} wins with ABSOLUTE WIN!")
            self.disable_board()
            return
        
        # Check if board is full
        if self.is_board_full():
            self.game_over = True
            self.update_display()  # Update display before logging/showing result
            if self.user_score > self.bot_score:
                self.log_game_result("User")
                messagebox.showinfo("Game Over", f"User wins with {self.user_score} points!")
            elif self.bot_score > self.user_score:
                self.log_game_result("Bot")
                messagebox.showinfo("Game Over", f"Bot wins with {self.bot_score} points!")
            else:
                self.log_game_result("tie")
                messagebox.showinfo("Game Over", "It's a tie!")
            self.disable_board()
            return
        
        # Handle turn switching
        self.handle_turn_switch()
        self.update_display()
    
    def handle_turn_switch(self):
        self.current_turn_count += 1
        
        if self.is_user_turn_phase:
            if self.current_turn_count >= self.turn_ratio[0]:
                self.is_user_turn_phase = False
                self.current_turn_count = 0
                self.current_player = 'O'
                # Bot's turn starts
                self.root.after(500, self.bot_move)
        else:
            if self.current_turn_count >= self.turn_ratio[1]:
                self.is_user_turn_phase = True
                self.current_turn_count = 0
                self.current_player = 'X'
    
    def bot_move(self):
        if self.game_over or not self.game_started:
            return
            
        if self.is_user_turn_phase:
            return
        
        # Advanced bot AI
        move = self.get_best_move()
        
        if move:
            if move[2]:  # Use spear
                self.use_spear_bot(move[0], move[1])
            else:
                self.make_bot_move(move[0], move[1])
        
    def get_best_move(self):
        # First, check if bot can win with absolute win
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == '':
                    self.board[row][col] = 'O'
                    if self.check_absolute_win() == 'O':
                        self.board[row][col] = ''
                        return (row, col, False)
                    self.board[row][col] = ''
        
        # Check if we need to block user's absolute win
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == '':
                    self.board[row][col] = 'X'
                    if self.check_absolute_win() == 'X':
                        self.board[row][col] = ''
                        return (row, col, False)
                    self.board[row][col] = ''
        
        # Check if we should use a spear
        if self.bot_spears > 0:
            spear_move = self.consider_spear_move()
            if spear_move:
                return spear_move
        
        # Use minimax for optimal move
        best_score = -math.inf
        best_move = None
        
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == '':
                    self.board[row][col] = 'O'
                    score = self.minimax(self.board, 0, False, -math.inf, math.inf)
                    self.board[row][col] = ''
                    
                    if score > best_score:
                        best_score = score
                        best_move = (row, col, False)
        
        return best_move
    
    def consider_spear_move(self):
        # Consider using spear on high-value user pieces
        best_value = 0
        best_pos = None
        
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == 'X':
                    value = self.point_values[row][col]
                    # Extra value if it's part of a potential winning line
                    if self.is_part_of_winning_threat(row, col, 'X'):
                        value += 50
                    
                    if value > best_value:
                        best_value = value
                        best_pos = (row, col, True)
        
        # Only use spear if the value is high enough
        return best_pos if best_value >= 40 else None
    
    def is_part_of_winning_threat(self, row, col, player):
        # Check if this position is part of a potential 3-in-a-row (only columns and diagonals)
        directions = [
            [(0,0), (1,0), (2,0)],  # Left column
            [(0,1), (1,1), (2,1)],  # Middle column
            [(0,2), (1,2), (2,2)],  # Right column
            [(0,0), (1,1), (2,2)],  # Main diagonal
            [(0,2), (1,1), (2,0)]   # Anti diagonal
        ]
        
        for line in directions:
            if (row, col) in line:
                count = sum(1 for r, c in line if self.board[r][c] == player)
                if count >= 2:
                    return True
        return False
    
    def minimax(self, board, depth, is_maximizing, alpha, beta):
        winner = self.check_absolute_win()
        if winner == 'O':
            return 1000 - depth
        elif winner == 'X':
            return -1000 + depth
        elif self.is_board_full():
            return self.bot_score - self.user_score
        
        if depth >= 6:  # Limit search depth
            return self.evaluate_position()
        
        if is_maximizing:
            max_eval = -math.inf
            for row in range(3):
                for col in range(3):
                    if board[row][col] == '':
                        board[row][col] = 'O'
                        eval_score = self.minimax(board, depth + 1, False, alpha, beta)
                        board[row][col] = ''
                        max_eval = max(max_eval, eval_score)
                        alpha = max(alpha, eval_score)
                        if beta <= alpha:
                            break
            return max_eval
        else:
            min_eval = math.inf
            for row in range(3):
                for col in range(3):
                    if board[row][col] == '':
                        board[row][col] = 'X'
                        eval_score = self.minimax(board, depth + 1, True, alpha, beta)
                        board[row][col] = ''
                        min_eval = min(min_eval, eval_score)
                        beta = min(beta, eval_score)
                        if beta <= alpha:
                            break
            return min_eval
    
    def evaluate_position(self):
        score = 0
        
        # Evaluate based on current points
        score += (self.bot_score - self.user_score)
        
        # Evaluate potential winning positions (only columns and diagonals)
        lines = [
            [(0,0), (1,0), (2,0)], [(0,1), (1,1), (2,1)], [(0,2), (1,2), (2,2)],  # Columns
            [(0,0), (1,1), (2,2)], [(0,2), (1,1), (2,0)]  # Diagonals
        ]
        
        for line in lines:
            bot_count = sum(1 for r, c in line if self.board[r][c] == 'O')
            user_count = sum(1 for r, c in line if self.board[r][c] == 'X')
            
            if user_count == 0:
                score += bot_count ** 2 * 10
            elif bot_count == 0:
                score -= user_count ** 2 * 10
        
        return score
    
    def make_bot_move(self, row, col):
        self.board[row][col] = 'O'
        self.buttons[row][col].config(text='O', bg='lightcoral')
        self.bot_score += self.point_values[row][col]
        
        # Log the move
        self.log_move(row, col, 'Bot')
        
        # Check for absolute win
        winner = self.check_absolute_win()
        if winner:
            self.game_over = True
            winner_name = 'User' if winner == 'X' else 'Bot'
            self.update_display()  # Update display before logging/showing result
            self.log_game_result(winner_name, "ABSOLUTE WIN")
            messagebox.showinfo("Game Over", f"{winner_name} wins with ABSOLUTE WIN!")
            self.disable_board()
            return
        
        # Check if board is full
        if self.is_board_full():
            self.game_over = True
            self.update_display()  # Update display before logging/showing result
            if self.user_score > self.bot_score:
                self.log_game_result("User")
                messagebox.showinfo("Game Over", f"User wins with {self.user_score} points!")
            elif self.bot_score > self.user_score:
                self.log_game_result("Bot")
                messagebox.showinfo("Game Over", f"Bot wins with {self.bot_score} points!")
            else:
                self.log_game_result("tie")
                messagebox.showinfo("Game Over", "It's a tie!")
            self.disable_board()
            return
        
        # Handle turn switching
        self.handle_turn_switch()
        self.update_display()
        
        # Continue bot moves if still bot's turn phase
        if not self.is_user_turn_phase and not self.game_over:
            self.root.after(1000, self.bot_move)
    
    def toggle_spear_mode(self):
        if not self.game_started or self.game_over:
            return
            
        if not self.is_user_turn_phase:
            messagebox.showwarning("Not Your Turn", "It's not your turn phase!")
            return
            
        if self.user_spears <= 0:
            messagebox.showwarning("No Spears", "You have no spears left!")
            return
        
        self.spear_mode = not self.spear_mode
        if self.spear_mode:
            self.spear_button.config(text="🎯 CANCEL SPEAR 🎯")
        else:
            self.spear_button.config(text="Use Spear")
        
        # Update button colors to indicate spear mode
        if self.spear_mode:
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == 'O':
                        self.buttons[row][col].config(bg='orange')
        else:
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == 'X':
                        self.buttons[row][col].config(bg='lightblue')
                    elif self.board[row][col] == 'O':
                        self.buttons[row][col].config(bg='lightcoral')
                    else:
                        self.buttons[row][col].config(bg='lightgray')
        
        # Update display to reflect spear mode changes
        self.update_display()
    
    def use_spear(self, row, col):
        if self.board[row][col] != 'O':
            messagebox.showwarning("Invalid Target", "You can only target bot's pieces!")
            return
        
        # Remove the piece and update score
        self.board[row][col] = ''
        self.buttons[row][col].config(text='', bg='lightgray')
        self.bot_score -= self.point_values[row][col]
        self.user_spears -= 1
        
        # Log the spear attack
        self.log_spear_attack(row, col, 'User')
        
        # Exit spear mode
        self.spear_mode = False
        self.spear_button.config(text="Use Spear")
        
        # Reset button colors
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == 'X':
                    self.buttons[r][c].config(bg='lightblue')
                elif self.board[r][c] == 'O':
                    self.buttons[r][c].config(bg='lightcoral')
                else:
                    self.buttons[r][c].config(bg='lightgray')
        
        # This counts as a turn
        self.handle_turn_switch()
        self.update_display()
    
    def use_spear_bot(self, row, col):
        if self.board[row][col] != 'X':
            return
        
        # Remove the piece and update score
        self.board[row][col] = ''
        self.buttons[row][col].config(text='', bg='lightgray')
        self.user_score -= self.point_values[row][col]
        self.bot_spears -= 1
        
        # Log the spear attack
        self.log_spear_attack(row, col, 'Bot')
        
        # This counts as a turn
        self.handle_turn_switch()
        self.update_display()
        
        # Continue bot moves if still bot's turn phase
        if not self.is_user_turn_phase and not self.game_over:
            self.root.after(1000, self.bot_move)
    
    def check_absolute_win(self):
        # Check columns (vertical wins only)
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                return self.board[0][col]
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return self.board[0][0]
        
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return self.board[0][2]
        
        return None
    
    def is_board_full(self):
        for row in self.board:
            for cell in row:
                if cell == '':
                    return False
        return True
    
    def update_display(self):
        self.user_score_label.config(text=f"User Score: {self.user_score}")
        self.bot_score_label.config(text=f"Bot Score: {self.bot_score}")
        self.user_spears_label.config(text=f"User Spears: {self.user_spears}")
        self.bot_spears_label.config(text=f"Bot Spears: {self.bot_spears}")
        
        if not self.game_started:
            self.turn_label.config(text="Game not started")
        elif self.game_over:
            self.turn_label.config(text="Game Over")
        elif self.spear_mode:
            self.turn_label.config(text="🎯 SPEAR MODE - Target bot's pieces! 🎯")
        else:
            phase = "User" if self.is_user_turn_phase else "Bot"
            moves_left = (self.turn_ratio[0] if self.is_user_turn_phase else self.turn_ratio[1]) - self.current_turn_count
            self.turn_label.config(text=f"{phase}'s turn phase - {moves_left} moves left")
        
        # Update spear button state
        if self.user_spears <= 0 or not self.is_user_turn_phase or self.game_over:
            self.spear_button.config(state='disabled')
        else:
            self.spear_button.config(state='normal')
    
    def disable_board(self):
        for row in self.buttons:
            for btn in row:
                btn.config(state='disabled')
        self.spear_button.config(state='disabled')
    
    def reset_game(self):
        # Reset game state
        self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        self.current_player = 'X'
        self.user_score = 0
        self.bot_score = 0
        self.game_started = False
        self.game_over = False
        self.current_turn_count = 0
        self.is_user_turn_phase = True
        self.spear_mode = False
        
        # Reset UI
        for row in self.buttons:
            for btn in row:
                btn.config(text='', bg='lightgray', state='disabled')
        
        self.start_button.config(state='normal')
        self.reset_button.config(state='normal')
        self.spear_button.config(text="Use Spear", state='disabled')
        
        # Clear log
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        self.update_display()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = AdvancedTicTacToe()
    game.run()