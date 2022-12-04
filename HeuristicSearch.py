# Grid of the board is 6x6
WIDTH1 = WIDTH2 = 6
GRID = WIDTH1 * WIDTH2


class HeuristicSearch:

    # Constructor
    def __init__(self, board, carDictionary, LAMBDA=4):
        self.board = board
        self.carDictionary = carDictionary
        self.LAMBDA = LAMBDA

    # --------------------------------------
    #              Heuristics
    # --------------------------------------

    # H1: The number of blocking vehicles
    # Determine number of blocking vehicle in front of the red car
    def h1(self):
        count_blocking_car = {}
        number_of_cars = 0

        # Red car is in 3rd row -> search this row
        i_after_red_car = self.carDictionary['A'][1] + self.carDictionary['A'][0]  # Determine the index after red car
        i_end_3rd_row = int((WIDTH1 * WIDTH2 / 2) - 1)

        if i_after_red_car - 1 == i_end_3rd_row:
            number_of_cars = len(count_blocking_car)
            return number_of_cars

        for n in range(i_after_red_car, i_end_3rd_row + 1):
            if self.board[n] != '.':
                count_blocking_car[self.board[n]] = 1

        number_of_cars = len(count_blocking_car)
        return number_of_cars

    # H2: The number of blocked positions
    # Determine number of blocking positions in front of the red car
    def h2(self):
        count_blocking_position = 0

        i_after_red_car = self.carDictionary['A'][1] + self.carDictionary['A'][0]
        i_end_3rd_row = int((WIDTH1 * WIDTH2 / 2) - 1)

        if i_after_red_car - 1 == i_end_3rd_row:
            return count_blocking_position

        for n in range(i_after_red_car, i_end_3rd_row + 1):
            if self.board[n] != '.':
                count_blocking_position = count_blocking_position + 1

        return count_blocking_position

    # H3: The value of h1 multiplied by a constant λ = 4
    def h3(self):
        return (self.h1() * self.LAMBDA)

    # H4: Admissible heuristic -> counts number of vertical vehicles + 1
    def h4(self):
        heuristicValue = 0

        # end of the third row (exit)
        i_end_3rd_row = int((WIDTH1 * WIDTH2 / 2) - 1)

        # the position after the AA car
        i_after_red_car = self.carDictionary['A'][1] + self.carDictionary['A'][0]

        # string to save the third row of the puzzle from car AA to the exit
        row = ''

        # getting the cars that are places between car AA and the exit
        for n in range(i_after_red_car, i_end_3rd_row + 1):
            if self.board[n] != '.':
                row+=self.board[n]

        # check the recorded row to indicate the direction of the cars in front of the AA car
        for c in row:
            # if a car name in "row" is only repeated once, that means that car is a vertical car
            if row.count(c) == 1:
                # for vertical cars in front of AA car, the value of "heuristicValue" will be increased by 1
                heuristicValue += 1

        heuristicValue = heuristicValue+1

        return heuristicValue
