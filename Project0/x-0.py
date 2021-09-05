# importing libs
import numpy as np
from random import randint
from IPython.display import clear_output

# init vars
FIELD_SIZE = 3
o = chr(0x25ef) # 'o'
x = chr(0x2715) # 'x'
cols = ['1', '2', '3']
rows = ['A', 'B', 'C']
results = {'-': "The game ended in a tie.",
           x: "Xs won!",
           o: "Os won!",
           None: "The game was cancelled"}
protocol = []

# Coverts addresses like 'A1' to (0, 0) and vice versa (from (2,1) to 'C2')
def conv_addr(*args):
    if type(args[0]) is tuple:
        return (rows[args[0][0]] + cols[args[0][1]])
    else:
        return (rows.index(args[0][0]), cols.index(args[0][1]))
        
# Prints playing field    
def print_field(field):
    clear_output()
    print('  |  {:4}{:4}{:4}'.format(*cols))
    print('-' * 15)
    for i in range(FIELD_SIZE):
        print(f'{rows[i]} |  ', end = '')
        for j in range(FIELD_SIZE):
            print(f'{field[i][j]:4}', end = '')
        print()
    print('-' * 15)

# Defining a rank for each cell.
# The rank is a number of columns, rows and diagonals (if any) linked with the cell, with no opponent's pieces in them. 
# The higher rank the more chances to win putting a piece there
# ** This is the main idea of the algorithm **
#
def ranking(field):
    ranks = {}
    # 'ranks' is a dictionary with cell's coordinates as its key, 
    # and a tuple as a value with two values in it - the first one is a rank for 'x', 
    # and the second one is a rank for 'o' for given cell.
    # the ranks are available for empty cells only
    for i in range(FIELD_SIZE):
        for j in range(FIELD_SIZE):
            x_rank, o_rank = 0, 0
            if field[i, j] == ' ':
                x_rank = 0 + (sum(field[i, :] == o) == 0) + (sum(field[:, j] == o) == 0)
                o_rank = 0 + (sum(field[i, :] == x) == 0) + (sum(field[:, j] == x) == 0)
                
                if i == j: 
                    x_rank += (sum(field.diagonal() == o) == 0)
                    o_rank += (sum(field.diagonal() == x) == 0)
                if (i, j) in [(0, 2), (1, 1), (2, 0)]: 
                    x_rank += (sum(field[::-1].diagonal() == o) == 0)
                    o_rank += (sum(field[::-1].diagonal() == x) == 0)
                    
                ranks[(i, j)] = (x_rank, o_rank)
    return ranks

# Checking if there is a win situation in the field
def check_win(field):
    for i in range(FIELD_SIZE):
        if sum(field[:, i] == x) == FIELD_SIZE \
            or sum(field[i, :] == x) == FIELD_SIZE \
            or sum(field.diagonal() == x) == FIELD_SIZE \
            or sum(field[::-1].diagonal() == x) == FIELD_SIZE:
                return(x)
        if sum(field[:, i] == o) == FIELD_SIZE \
            or sum(field[i, :] == o) == FIELD_SIZE \
            or sum(field.diagonal() == o) == FIELD_SIZE \
            or sum(field[::-1].diagonal() == o) == FIELD_SIZE:
                return(o)

    if ' ' not in field:
        return "-"
    
    # If there is a winner, return it's character, if no empty cells return '-', otherwise return None
    return None

# Make an AI move 
def move(field):
    # a copy of the field for simulating outcomes of the next move
    next_try = field[:]
    for i in range(FIELD_SIZE):
        for j in range(FIELD_SIZE):
            if next_try[i, j] == ' ': 
                # Rule 1. Check if we can win on the next move and make that move if it exists
                next_try[i, j] = me
                if check_win(next_try) == me:
                    return(rows[i]+cols[j])
                # Rule 2. check if the opponent can win on the next move, and make this move to defend
                next_try[i, j] = you
                if check_win(next_try) == you:
                    return(rows[i]+cols[j])
                next_try[i, j] = ' '

    # Rule 3. Use the middle cell if it is empty
    if field[FIELD_SIZE // 2, FIELD_SIZE // 2] == ' ':
        return(rows[FIELD_SIZE // 2]+cols[FIELD_SIZE // 2])
    
    # Rule 4. Trying to deliver a fork tactic using the cells' ranks
    moves = []
    ranks = ranking(field)
    x_max = sorted(ranks.items(), key=lambda item: item[1][0], reverse=True)[0][1][0] # max for x
    o_max = sorted(ranks.items(), key=lambda item: item[1][1], reverse=True)[0][1][1] # max for o

    for i in ranks.items():
        if i[1][0] == x_max and me == x:
            moves.append(i[0])
        if i[1][1] == o_max and me == o:
            moves.append(i[0])
    
    return (conv_addr(moves[randint(0, len(moves)-1)]))

def ask(prompt, options):
    while True:
        response = input(prompt).upper()
        if response in options:
            return(response)
        else:
            print("Wrong input! Options available are:", options)

# init playing field and ranks dictionary
# playing_field is matrix 3 x 3
# 

if ask("Would you like to start? [Y/n]?", ['Y', 'N', '']) == 'N':
    me, you = x, o
else:
    me, you = o, x


step = x
playing_field = np.array([' '] * (FIELD_SIZE*FIELD_SIZE)).reshape(FIELD_SIZE, FIELD_SIZE)
ranks = ranking(playing_field)
protocol.append(['you', you])

cells_available = []
for each in ranks.keys():
    cells_available.append(rows[each[0]]+cols[each[1]])

print_field(playing_field)

# main cycle
while not check_win(playing_field):
    if step == you:
        cell = ask("Your turn: [:q to exit]", cells_available+[':Q'])
    else:
        cell = move(playing_field)
        
    if cell == ':Q':
        break

    protocol.append([step, cell])
    playing_field[conv_addr(cell)] = you if step == you else me
    cells_available.remove(cell)
    ranks = ranking(playing_field)
    
    print_field(playing_field)
    step = o if step == x else x

print("Results:", results[check_win(playing_field)])
print(protocol)