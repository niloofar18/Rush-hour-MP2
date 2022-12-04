import os

WIDTH1 = WIDTH2 = 6
SEARCH_FILES = 'outputs/search'
SOLUTION_FILES = 'outputs/solution'
FILE = 'input'


#######################################
#    Method for Output to Files
#######################################
def new_path_sol(state):
    arr = []

    while state.parent is not None:
        arr.append(state.activity)
        state = state.parent
    return '; '.join(arr[::-1])


def board_output(board):
    arr = ''

    for j in range(WIDTH1, (WIDTH1 * WIDTH2 + 1), WIDTH1):
        arr += ' '.join(board[j - WIDTH1:j]) + '\n'
    return arr


def new_records_fuel(carDictionary):
    arr = ''

    for cars in carDictionary:
        arr += f'{cars}:{carDictionary[cars][2]} '
    return arr


def show_path_sol(state):
    arr = []
    solution_files = []
    counter = 0

    while state.parent is not None:
        counter += 1
        solution_files.append([state.activity, state.board, state.carDictionary])
        state = state.parent

    solution_files = solution_files[::-1]
    records_fuel = ''
    fuel_of_car = {}

    for path in solution_files:
        board = path[1]
        activity = path[0].split(' ')
        carDictionary = path[2]
        cars = activity[0]
        fuel_of_car[cars] = carDictionary[cars][2]
        records_fuel = ''

        for i in fuel_of_car:
            records_fuel += f'{i}{fuel_of_car[i]} '
        arr.append(f'{cars}{activity[1]:>6} {activity[2]} \t{fuel_of_car[cars]:>2} {board} {records_fuel}')
    return counter, '\n'.join(arr), records_fuel


#######################################
#    Method for Creating the Files
#######################################

# --------------------------------------
# Function to create the solution files
# --------------------------------------
def file_create_solution(game, method, file_id, length_search, h):
    output = f'{SOLUTION_FILES}/{method}-sol-{file_id}.txt'
    if h != '':
        output = f'{SOLUTION_FILES}/{method}-{h}-sol-{file_id}.txt'

    if not os.path.exists(SOLUTION_FILES):
        os.makedirs(SOLUTION_FILES)

    with open(output, 'w') as f:
        if game.node_solution is not None:
            length_sol, path_new, records_fuel = show_path_sol(game.node_solution)
            f.write(f'Initial Board Configuration: {game.board}\n\n')
            f.writelines(board_output(game.board))
            f.write(f'\nCar Fuel Available: {new_records_fuel(game.carDictionary)}\n\n')
            f.write(f'Runtime: {game.runtime}\n')
            f.write(f'Search Path Length: {length_search}\n')
            f.write(f'Solution Path Length: {length_sol}\n')
            f.write(f'Solution Path: {new_path_sol(game.node_solution)}\n\n')
            f.writelines(path_new)
            f.write(f'\n\n! {records_fuel}\n')
            f.writelines(f'{board_output(game.node_solution.board)}')
        else:
            f.write(f'Initial Board Configuration: {game.board}\n\n')
            f.writelines(board_output(game.board))
            f.write(f'\nCar Fuel Available: {new_records_fuel(game.carDictionary)}\n\n')
            f.write('Puzzle cannot be solved. \nError: No Solution\n\n')
            f.write(f'Runtime: {game.runtime}\n')

# --------------------------------------
# Function to create the search files
# --------------------------------------
def file_create_search(close, method, file_id, h):
    hn = 0
    fn = 0
    gn = 0
    arr = []
    search_files = []

    for key in close.keys():
        search_files.append(key)

    car_start = search_files.pop(0)

    # ----------------------------------
    # Search path is being sorted
    # ----------------------------------
    if method == 'ucs':
        gn = fn = car_start.cost_path
        search_files.sort(key=lambda x: x.cost_path)

    elif method == 'gbfs':
        hn = fn = car_start.h_cost
        search_files.sort(key=lambda x: x.h_cost)

    elif method == 'a':
        hn = car_start.h_cost
        fn = car_start.entire_cost
        gn = car_start.cost_path
        search_files.sort(key=lambda x: x.entire_cost)

    arr.append(f'{fn:>2} {gn:>2} {hn:>2} {car_start.board}')

    for state in search_files:
        board = state.board
        carDictionary = state.carDictionary
        records_fuel = ''

        if method == 'ucs':
            gn = fn = state.cost_path
        elif method == 'gbfs':
            hn = fn = state.h_cost
        elif method == 'a':
            hn = state.h_cost
            fn = state.entire_cost
            gn = state.cost_path

        while state.parent is not None:
            cars = state.activity[0]
            records_fuel += f'{cars} {carDictionary[cars][2]} '
            state = state.parent
        arr.append(f'{fn:>2} {gn:>2} {hn:>2} {board} {records_fuel}')
    show_result = '\n'.join(arr)
    output = f'{SEARCH_FILES}/{method}-search-{file_id}.txt'

    if h != '':
        output = f'{SEARCH_FILES}/{method}-{h}-search-{file_id}.txt'

    if not os.path.exists(SEARCH_FILES):
        os.makedirs(SEARCH_FILES)

    with open(output, 'w') as f:
        f.writelines(show_result)


# --------------------------------------
# Function to create the analysis table
# --------------------------------------
def generateAnalysis(the_info_list):
    # creating a table for the analysis
    analysisF = open('analysis.txt', 'w')

    analysisF.write("Puzzle   Algorithm   Heuristic   Length of the   Length of the   Execution Time\n")
    analysisF.write("Number                                Solution     Search Path     (in seconds)\n")
    analysisF.write("--------------------------------------------------------------------------------\n")



    number_of_puzzles = int(len(the_info_list)/9)

    for i in range(1, number_of_puzzles+1):
        for info in the_info_list:

            # to indicate the puzzle number
            if info[0] != i:
                continue

            if info[3]==" ":
                continue

            # If the runtime is too small, 4 decimals will be shown
            gameTime = ''
            if str("{:4.2f}".format(info[5])) == '0.00':
                gameTime = str("{:4.4f}".format(info[5]))
            else:
                gameTime = str("{:4.2f}".format(round(info[5], 2)))

            analysisF.write(str(info[0]))
            analysisF.write(" " * (9 - len(str(info[0]))))

            analysisF.write(info[1])
            analysisF.write(" " * (12 - len(info[1])))

            analysisF.write(info[2])
            analysisF.write(" " * (12 - len(info[2])))

            analysisF.write(" " * (16 - len(str(info[3]))))
            analysisF.write(str(info[3]))

            analysisF.write(" " * (12 - len(str(info[4]))))
            analysisF.write(str(info[4]))

            analysisF.write(" " * (14 - len(gameTime)))
            analysisF.write(gameTime)
            analysisF.write("\n")

        analysisF.write("\n")

    analysisF.close()




