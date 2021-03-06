import sys
import re
from tabulate import tabulate
import random

BOARD_MAX_COL = 10
BOARD_MAX_ROW = 10
RED = 1
YELLOW = -1

board_size = (7, 6)
board_size_input = ''
two_player = True

if len(sys.argv) == 1:
	print("What board dimensions would you like? (7, 6)")
	board_size_input = input()
else:
	for arg in sys.argv[1:]:
		if arg == "/cpu":
			two_player = False
		else:
			board_size_input = arg

def parse_input(_input, col_max, row_min):
	match = re.match('^\(?\s*(\d+)\s*(,|x)\s*(\d+)\s*\)?$', _input)
	if match:
		return (min(int(match.group(1)), col_max), min(int(match.group(3)), row_min))
	return None

if board_size_input:
	board_size = parse_input(board_size_input, BOARD_MAX_COL, BOARD_MAX_ROW) or board_size # None coalesce

board = [['_' for x in range(board_size[0])] for y in range(board_size[1])]

def print_board(board, board_size):
	print(tabulate(board,
		headers=[h for h in range(board_size[0])]))
	print('\n')

def board_is_full(board, board_size):
	for col in range(board_size[0]):
		if board[0][col] == '_':
			return False
	return True

def move_core(board, board_size, player, col):
	row = 0
	for i in range(board_size[1]-1, -1, -1):
		if (board[i][col] == '_'):
			board[i][col] = 'R' if player==1 else 'Y'
			row = i
			break
	return (player, col, row)

def move(board, board_size, player):
	output = 'RED' if player==RED else 'YELLOW'
	col = min(board_size[0] - 1, int(input(output + ' >> ')))
	if board[0][col] != '_':
		return move(board, board_size, player) # ask again
	return move_core(board, board_size, player, col)

def move_cpu(board, board_size, player):
	output = 'RED' if player==RED else 'YELLOW'
	col = random.choice(range(board_size[0]))
	print(output, '>>', col)
	if board[0][col] != '_':
		return move_cpu(board, board_size, player) # try again
	return move_core(board, board_size, player, col)

def check_is_win_direction(board, player_code, col, row, args):
	success = 0 # don't include starting value
	
	xmod, ymod, condition = args
	x, y = col+xmod, row+ymod
	while condition(x, y):
		if board[y][x] != player_code:
			break
		success += 1
		x += xmod
		y += ymod

	return success

def check_is_win_core(board, player_code, col, row, pos_args, neg_args): 
	success = 1 # include starting value

	# check positive
	success += check_is_win_direction(board, player_code, col, row, pos_args)

	if success >= 4:
		return True # return early

	if neg_args is None:
		return success >= 4 # some consumers may be unidirectional

	# check neg
	success += check_is_win_direction(board, player_code, col, row, neg_args)

	return success >= 4

def check_is_win_horizontal(board, board_size, player_code, col, row):
	pos_args = (1, 0, lambda x, y : x < board_size[0] and y == row)
	neg_args = (-1, 0, lambda x, y : x > -1 and y == row)
	return check_is_win_core(board, player_code, col, row, pos_args, neg_args)

def check_is_win_vertical(board, board_size, player_code, col, row):
	pos_args = (0, 1, lambda x, y : y < board_size[1] and x == col)
	return check_is_win_core(board, player_code, col, row, pos_args, None)

def check_is_win_posdiagonal(board, board_size, player_code, col, row): # /
	pos_args = (1, -1, lambda x, y : x < board_size[0] and y >= 0)
	neg_args = (-1, 1, lambda x, y : x >= 0 and y < board_size[1])
	return check_is_win_core(board, player_code, col, row, pos_args, neg_args)

def check_is_win_negdiagonal(board, board_size, player_code, col, row): # \
	pos_args = (-1, -1, lambda x, y : x >= 0 and y >= 0)
	neg_args = (1, 1, lambda x, y : x < board_size[0] and y < board_size[1])
	return check_is_win_core(board, player_code, col, row, pos_args, neg_args)

def is_winning_move(board, board_size, _move):
	player, col, row = _move
	player_code = 'R' if player==RED else 'Y'
	return (check_is_win_horizontal(board, board_size, player_code, col, row)
		or check_is_win_vertical(board, board_size, player_code, col, row)
		or check_is_win_posdiagonal(board, board_size, player_code, col, row)
		or check_is_win_negdiagonal(board, board_size, player_code, col, row))
	
def start(board, board_size):
	moves = []
	print_board(board, board_size)

	player = RED # Red goes first
	curr_move = move(board, board_size, player)
	moves.append(curr_move)
	print_board(board, board_size)
	while not is_winning_move(board, board_size, curr_move):
		if board_is_full(board, board_size):
			return None

		player *= -1 # Switch player
		curr_move = move(board, board_size, player)
		moves.append(curr_move)
		print_board(board, board_size)

	return player 
	
def start_cpu(board, board_size):
	moves = []
	cpu_code = random.choice([RED, YELLOW])
	human_code = cpu_code * -1
	print("You are", "RED!" if human_code == RED else "YELLOW!")
	player = human_code if human_code == RED else cpu_code # Red goes first	 
	
	print_board(board, board_size)
	if player == human_code:
		curr_move = move(board, board_size, player)
	else:
		curr_move = move_cpu(board, board_size, player)
	moves.append(curr_move)
	print_board(board, board_size)
	while not is_winning_move(board, board_size, curr_move):
		if board_is_full(board, board_size):
			return None

		player *= -1 # Switch player
		if player == human_code:
			curr_move = move(board, board_size, player)
		else:
			curr_move = move_cpu(board, board_size, player)
		moves.append(curr_move)
		print_board(board, board_size)

	return player

if two_player:
	winner = start(board, board_size)
else:
	winner = start_cpu(board, board_size)

if winner is None:
	print("It's a TIE!!")
elif winner == RED:
	print("RED Wins!!")
elif winner == YELLOW:
	print("YELLOW Wins!!")
