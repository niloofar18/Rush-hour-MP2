# This class represents the parent and its children info

# Grid of the board is 6x6
WIDTH1 = WIDTH2 = 6
GRID = WIDTH1 * WIDTH2


class State:

    # Constructor
    def __init__(self, parent, cost_path, carDictionary, board, activity):
        self.board = board
        self.carDictionary = carDictionary
        self.parent = parent
        self.activity = activity
        self.cost_path = cost_path
        self.entire_cost = 0
        self.h_cost = 0

    # Use this function to have a new board updated
    def new_board_updated(self, board, move, coordination, car_start, car_end, car_step):
        start, end = car_start, car_end
        car_step = car_step * coordination
        board = [*board]

        for j in range(move):
            if coordination == 1:
                board[start], board[end + car_step] = board[end + car_step], board[start]
            else:
                board[end], board[start + car_step] = board[start + car_step], board[end]
            start += car_step
            end += car_step

        board = ''.join(board)
        return board[:GRID], start

    # Calculate the entire cost (path + heuristic)
    def set_h_cost(self, h):
        self.h_cost = h
        self.entire_cost = self.cost_path + h

    # Using key for hash and quality function
    def __key(self):
        return self.board

    # Determine if the cost of one object is less than the cost of other object
    def __lt__(self, other):
        return self.cost_path < other.cost_path

    # Compare dictionary's key & used to insert objects into dictionary
    def __hash__(self):
        return hash(self.__key())

    # Determine if current state is equal to the visited state (node)
    def __eq__(self, other):
        if isinstance(other, State):
            return self.__key() == other.__key()
        return NotImplemented

    # If the puzzle contains AA then it is in goal state
    def is_goal_aa(self, board):
        goal_game = board[16:18]
        return goal_game == 'AA'

    # Calculate the info about children of each parent state
    def children_tree(self):
        # This keeps the list of parent, board, cars and entire cost of each state
        child = []

        # For every car in car Dictionary
        for cars in self.carDictionary:
            length_car, i, fuel, direction, is_car_exit = self.carDictionary[cars]
            car_exit = False

            # skipping the cars with fuel level of zero or below zero
            if fuel <= 0:
                continue

            (empty_position) = self.get_position(length_car, direction, i)

            # we choose to use numeric value for coordinates: (right=1, left=-1, up=1, down=-1)
            move_coordinate = (1, -1)
            state = None

            # Determine every possible board for each movement of each car
            for empty_p, move_c in zip(empty_position, move_coordinate):
                length_maximum = empty_p if empty_p < fuel else fuel

                if move_c == 1:
                    activity_m = 'down' if direction == 'v' else 'right'
                else:
                    activity_m = 'up' if direction == 'v' else 'left'

                car_start, car_end, car_step = i, WIDTH2 * (
                            length_car - 1) + i if direction == 'v' else i + length_car - 1, WIDTH2 if direction == 'v' else 1

                for move in range(length_maximum, 0, -1):
                    fuel1 = fuel
                    if fuel1 < move:
                        continue
                    fuel1 -= move

                    # Remove the movement if it is horizontal -> goal position
                    activity = f'{cars} {activity_m} {move}'

                    board_new, i_new = self.new_board_updated(self.board, move, move_c, car_start, car_end, car_step)

                    # This is the goal state, child's state has the move, so we move back to the top
                    if self.is_goal_aa(board_new):
                        carDictionary_new = self.carDictionary.copy()
                        carDictionary_new[cars] = (length_car, i_new, fuel1, direction, True)
                        state = State(self, self.cost_path + 1, carDictionary_new, board_new, activity)
                        return [state]

                    # The car is in exit state, so we remove it
                    if board_new[17] == cars and direction == 'h':
                        board_new = board_new.replace(cars, '.')
                        car_exit = True

                    carDictionary_new = self.carDictionary.copy()
                    carDictionary_new[cars] = (length_car, i_new, fuel1, direction, True)
                    state = State(self, self.cost_path + 1, carDictionary_new, board_new, activity)
                    child.append(state)

                    if car_exit:
                        break
                if car_exit:
                    break
        return child

    # -------------------------------------------------------------------------
    # BFS of each child of a parent state
    def best_first_search_child(self):
        grid = [[self.board[m + (n * WIDTH1)] for m in range(WIDTH1)] for n in range(WIDTH2)]
        return []

    # -------------------------------------------------------------------------

    # Output all members (board + movement)
    def __str__(self):
        return (f'Board: {self.board}, Move: {self.activity}')

    def get_empty_position(self, car_start, car_end, car_step):
        empty_position = 0
        for n in range(car_start, car_end, car_step):
            if self.board[n] == '.':
                empty_position += 1
            else:
                break
        return empty_position

    # Determine how many position we have around our car
    def get_position(self, length_car, direction, position):

        # To record the empty position at the front and back of the car
        front_empty_position = 0
        back_empty_position = 0

        # For vertical cars, coordination is either going up or either going down
        if direction == 'v':
            up, down = position, WIDTH2 * (length_car - 1) + position
            # finding the upper border
            up_border = up % WIDTH1
            # finding the bottom border
            down_border = (up % WIDTH1) + GRID - WIDTH2

            # if we are at the top corner of the board -> go down
            if down < down_border:
                front_empty_position = self.get_empty_position((down + WIDTH2), (down_border + 1), WIDTH2)

            # if we are at the bottom corner of the board -> go up
            if up > up_border:
                back_empty_position = self.get_empty_position((up - WIDTH2), (up_border - 1), -WIDTH2)

        # For horizontal cars coordination is either going left or either going right
        else:
            go_left, go_right = position, (position + length_car - 1)
            left_border = int(go_left / WIDTH1) * WIDTH1
            right_border = (int(go_left / WIDTH1) * WIDTH1) + WIDTH1

            if go_right < right_border - 1:
                front_empty_position = self.get_empty_position((go_right + 1), right_border, 1)
            if go_left > left_border:
                back_empty_position = self.get_empty_position((go_left - 1), (left_border - 1), -1)

        return front_empty_position, back_empty_position
