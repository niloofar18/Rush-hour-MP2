from Game import Game
from queue import PriorityQueue
from State import State
from HeuristicSearch import HeuristicSearch
import time
import os
import copy
import argparse

import FileGenerators
import PuzzleGenerator

WIDTH1 = WIDTH2 = 6
SEARCH_FILES = 'outputs/search'
SOLUTION_FILES = 'outputs/solution'
FILE = 'input'


# -----------------------------------------------
#        Determine the fuel for each car
# -----------------------------------------------
def get_fuel(cars, records_fuel):
    for fuels in records_fuel:
        if cars == fuels[0]:
            return int(fuels[1])
    return 100


# Know the direction of each car (Vertical or Horizontal)
def get_direction(car, grid):
    direction = 'v'

    harizontal_version = car + car
    if harizontal_version in grid:
        direction = 'h'

    return direction


# ---------------------------------------------------
#     Car Dictionary including its car & length
# ---------------------------------------------------
def get_carDictionary(board, records_fuel):
    carDictionary = {}

    for n, car in enumerate(board):
        if car != '.' and car not in carDictionary.keys():
            carDictionary[car] = (board.count(car), n, get_fuel(car, records_fuel), get_direction(car, board), False)
    return carDictionary


# function to save a list of the activity of all the ancestors of a given state
def get_solution_files(state):
    activities = []

    # saving the activity for all the ancestors of this state
    while state.parent is not None:
        activity = [state.board, state.activity, state.carDictionary]
        activities.append(activity)
        state = state.parent
    return activities[::-1]


# --------------------------------------------
#             Uniform Cost Search
# --------------------------------------------
def ucs_method(game):
    time0 = time.time()

    # close list is a dictionary of current states as the keys with cost_path as values
    close = {}

    # 'open_queue' save values in forms of tuples of (cost_path, state)
    open_queue = PriorityQueue()

    # As we are looking for the shortest path, we initially set the len_of_path_minimum to infinity (the biggest int)
    len_of_path_minimum = float('inf')

    # Creating the root state
    car_start = State(None, 0, game.carDictionary, game.board, 'start')

    # Adding the root/start state to the open list
    open_queue.put((0, car_start))

    # while open queue is not empty
    while not open_queue.empty():

        cost_path, state_current = open_queue.get(block=False)

        # check if there is another version of this state in the open_queue
        inside_open_set, i = verify_open_set(open_queue, state_current)

        # if our current_state cost is bigger than our best cost -> put in close list
        if game.node_solution is not None:
            if state_current.cost_path >= game.node_solution.cost_path:
                close[state_current] = cost_path
                continue

        # If it is in close state -> ignore it
        if state_current in close:
            continue

        # If it is in open state then replace if the path is better
        elif inside_open_set:
            if cost_path < open_queue.queue[i][0]:
                open_queue.queue[i] = (cost_path, state_current)
            continue

        # check if the board is in goal state
        elif game.is_goal_aa(state_current.board):

            # if 'node_solution' already has a value
            if game.node_solution is not None:

                # Replace node_solution if cost of this state is better
                if cost_path < game.node_solution.cost_path:

                    game.node_solution = state_current

                    # put this state in cloe list
                    close[state_current] = cost_path

                    continue

            # else, save current state as the node_solution
            else:

                game.node_solution = state_current
                close[state_current] = cost_path

                continue

            continue

        else:

            # Move this state to the close list and generate its successors
            close[state_current] = cost_path
            child = state_current.children_tree()

            # for every child/successor
            for c in child:

                # check if another version of 'c' is already in open list
                inside_open_set, i = verify_open_set(open_queue, c)

                # if there is a version in close list -> if old version has higher cost, remove it
                if c in close:
                    if c.cost_path < close[c]:
                        close.pop(c)
                    else:
                        continue

                # adding new version to the open queue
                open_queue.put((c.cost_path, c))

    # recording the runtime
    game.runtime = time.time() - time0

    return len_of_path_minimum, close


# ---------------------------------
#             GBFS
# ---------------------------------
def gbfs_method(game, h):
    time0 = time.time()
    close = {}

    # values of open-queue are saved as a tuple of the following format -> (entire_cost, state)
    open_queue = PriorityQueue()

    # As we are looking for the shortest path, we initially set the len_of_path_minimum to infinity (the biggest int)
    len_of_path_minimum = float('inf')

    heuristicSearch = HeuristicSearch(game.board, game.carDictionary)

    # Creating the root state
    car_start = State(None, 0, game.carDictionary, game.board, 'start')
    cost_heuristic = eval(f'heuristicSearch.{h}()')
    car_start.set_h_cost(cost_heuristic)

    # Adding the root (starting state) to the open_queue
    open_queue.put((0, car_start))

    # while open_queue is not empty
    while not open_queue.empty():
        h_cost, state_current = open_queue.get(block=False)

        # If cost of current_state is bigger than cost of the solution node -> place current state in the close list
        if game.node_solution is not None:
            if state_current.h_cost >= game.node_solution.h_cost:
                close[state_current] = h_cost
                continue

        # If current state is in close list -> ignore
        if state_current in close:
            continue

        # else if this state is a goal state
        elif game.is_goal_aa(state_current.board):

            # If another state is already saved as node_solution
            if game.node_solution is not None:

                # replace node_solution with this state if this state has a lower cost
                if state_current.cost_path < game.node_solution.cost_path:

                    game.node_solution = state_current

                    # put current_state in the close list
                    close[state_current] = state_current.h_cost

                    continue

            # else, save current state as the node_solution
            else:

                solution_files, len_of_path_minimum = this_is_goal(game, state_current, len_of_path_minimum)
                game.solution_files = solution_files
                game.node_solution = state_current

            continue

        else:

            # Move this state to the close list and generate its successors
            close[state_current] = h_cost
            child = state_current.children_tree()

            # For each successor/child
            for c in child:
                heuriscticSearch = HeuristicSearch(c.board, c.carDictionary)

                # set the heuristic cost
                cost_heuristic = eval(f'heuristicSearch.{h}()')
                c.set_h_cost(cost_heuristic)

                # check if another version of 'c' is already in open list
                inside_open_set, i = verify_open_set(open_queue, c)

                # if c is already in close list -> ignore new version
                if c in close:
                    if c.cost_path < close[c]:
                        continue
                # if c is already in open list -> ignore new version
                elif inside_open_set:
                    continue

                # add child 'c' to the open queue
                open_queue.put((c.h_cost, c))

    game.runtime = time.time() - time0

    return len_of_path_minimum, close


# ------------------------------------------------------------------------------
#        A / A* -> If h is not admissible, then it is A; otherwise it's A*
# ------------------------------------------------------------------------------
def a_method(game, h):
    time0 = time.time()
    close = {}

    # values of open-queue are saved as a tuple of the following format -> (entire_cost, state)
    open_queue = PriorityQueue()

    # As we are looking for the shortest path, we initially set the len_of_path_minimum to infinity (the biggest int)
    len_of_path_minimum = float('inf')

    heuristicSearch = HeuristicSearch(game.board, game.carDictionary)

    # Creating the root state
    car_start = State(None, 0, game.carDictionary, game.board, 'start')
    cost_heuristic = eval(f'heuristicSearch.{h}()')
    car_start.set_h_cost(cost_heuristic)

    # Adding the root (starting state) to the open_queue
    open_queue.put((0, car_start))

    # while open_queue is not empty
    while not open_queue.empty():
        entire_cost, state_current = open_queue.get(block=False)
        inside_open_set, i = verify_open_set(open_queue, state_current)

        # If cost of current state is bigger than cost of the solution node -> place current state in close list
        if game.node_solution is not None:

            if state_current.entire_cost >= game.node_solution.entire_cost:
                close[state_current] = entire_cost
                continue

        # Ignore this state if it is in close state
        if state_current in close:
            continue

        # If another version of it is already in open list
        elif inside_open_set:

            # If that version has a higher cost, replace it with this state
            if entire_cost < open_queue.queue[i][0]:
                open_queue.queue[i] = (entire_cost, state_current)
            continue

        # In case this state is in the goal state
        elif game.is_goal_aa(state_current.board):

            # If a state is already saved as node_solution
            if game.node_solution is not None:

                # Choose the state with the lowest cost-path as the node_solution
                if state_current.cost_path < game.node_solution.cost_path:

                    game.node_solution = state_current

                    # Then move the visited state to the close list
                    close[state_current] = state_current.entire_cost
                    continue

            # If solution node is empty, then set this state as the node_solution
            else:

                solution_files, len_of_path_minimum = this_is_goal(game, state_current, len_of_path_minimum)
                game.solution_files = solution_files
                game.node_solution = state_current

            continue

        else:

            # Move this state to the close list and generate its successors
            close[state_current] = entire_cost
            child = state_current.children_tree()

            for c in child:

                heuriscticSearch = HeuristicSearch(c.board, c.carDictionary)
                cost_heuristic = eval(f'heuristicSearch.{h}()')
                c.set_h_cost(cost_heuristic)

                inside_open_set, i = verify_open_set(open_queue, c)

                # if successor c is in close list with higher cost, replace old version with new c
                if c in close:
                    if close[c] > c.entire_cost:

                        close.pop(c)

                    else:
                        continue

                # if successor c is in open list with higher cost, replace old version with new c
                if inside_open_set:
                    if c.entire_cost < open_queue.queue[i][0]:

                        open_queue.queue.pop(i)

                    else:
                        continue

                open_queue.put((c.entire_cost, c))

    game.runtime = time.time() - time0

    return len_of_path_minimum, close


# --------------------------
def this_is_goal(game, c, len_of_path_minimum):
    # Finding the length of solution path of state c
    activities = get_solution_files(c)
    length_solution_files = len(activities)

    # to record the solution file
    solution_files = []

    # Check if state 'c' has a shorter solution path
    if length_solution_files < len_of_path_minimum:
        len_of_path_minimum = length_solution_files
        fuels = ''

        for activity in activities:
            cars = activity[1][0]
            fuels = f'{cars} {activity[2][cars][2]}' + f' {fuels}'
            solution_files.append(activity[1])

        # setting state 'c' as the node_solution
        game.node_solution = c

    return solution_files, len_of_path_minimum


# function to check if the board of a state is not already generated (to prevent loops)
def verify_open_set(open_queue, state):
    for n, check in enumerate(open_queue.queue):
        if check[1].board == state.board:
            return True, n
    return False, None


if __name__ == '__main__':

    # Generating 50 random puzzles of 6x6
    PuzzleGenerator.creatPuzzles(50, 36)

    pars_argument = argparse.ArgumentParser()
    pars_argument.add_argument('--file', '-f', type=str, default='generatedPuzzles.txt') # Default name of puzzles' file

    argument = pars_argument.parse_args()
    input = f'{FILE}/{argument.file}'

    tests = []

    # Start reading the file
    with open(input, 'r') as f:
        for line in f.readlines():
            word = line.strip().split(' ')
            if word[0] == '#' or word[0] == '':
                continue
            tests.append(word)

    records_game = []

    # tests goes through game
    for test in tests:
        board = test[0]
        carDictionary = get_carDictionary(board, test[1:])
        records_game.append(Game(board, carDictionary))

    methods = ['ucs', 'gbfs', 'a']
    heuristicSearch = ['h1', 'h2', 'h3', 'h4']

    # An array to save the info needed for generating the analysis table
    analysisList = []

    for method in methods:
        for n, game in enumerate(records_game):
            if method == 'ucs':
                copy_game = copy.deepcopy(game)
                len_of_path_minimum, close = ucs_method(copy_game)
                FileGenerators.file_create_search(close, method, (n + 1), '')
                FileGenerators.file_create_solution(copy_game, method, (n + 1), len(close), '')

                # Adding the info to the analysis list
                if copy_game.node_solution is not None:
                    length_sol, path_new, records_fuel = FileGenerators.show_path_sol(copy_game.node_solution)
                    analysisList.append([n + 1, method.upper(), "NA", length_sol, len(close), copy_game.runtime])
                else:
                    analysisList.append([n + 1, method.upper(), "NA", " ", " ", copy_game.runtime])

            elif method == 'gbfs':
                for h in heuristicSearch:
                    copy_game = copy.deepcopy(game)
                    len_of_path_minimum, close = gbfs_method(copy_game, h)
                    FileGenerators.file_create_search(close, method, (n + 1), h)
                    FileGenerators.file_create_solution(copy_game, method, (n + 1), len(close), h)

                    # Adding the info to the analysis list
                    if copy_game.node_solution is not None:
                        length_sol, path_new, records_fuel = FileGenerators.show_path_sol(copy_game.node_solution)
                        analysisList.append([n + 1, method.upper(), h, length_sol, len(close), copy_game.runtime])
                    else:
                        analysisList.append([n + 1, method.upper(), h, " ", " ", copy_game.runtime])

            elif method == 'a':
                for h in heuristicSearch:
                    copy_game = copy.deepcopy(game)
                    len_of_path_minimum, close = a_method(copy_game, h)
                    FileGenerators.file_create_search(close, method, (n + 1), h)
                    FileGenerators.file_create_solution(copy_game, method, (n + 1), len(close), h)

                    # Adding the info to the analysis list
                    if copy_game.node_solution is not None:
                        length_sol, path_new, records_fuel = FileGenerators.show_path_sol(copy_game.node_solution)
                        analysisList.append([n + 1, 'A/A*', h, length_sol, len(close), copy_game.runtime])
                    else:
                        analysisList.append([n + 1, 'A/A*', h, " ", " ", copy_game.runtime])
                continue

#------------------------------------------
#      Generating the analysis table
# -----------------------------------------
    FileGenerators.generateAnalysis(analysisList)

    # saving the displayed puzzles in a 'PuzzleBoards.txt' -> for analysis purposes
    displayp = open('puzzleBoards.txt', 'a')
    puzzleNum = 1

    for test in tests:
        puzzleBoard = test[0]
        displayp.write("\n\n**** Puzzle ")
        displayp.write(str(puzzleNum))
        displayp.write("\n\n")
        for i in range(7):
            displayp.write(puzzleBoard[(i - 1) * 6:6 * i])
            displayp.write("\n")
        puzzleNum += 1

    displayp.close()
