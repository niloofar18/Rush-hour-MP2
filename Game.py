class Game:

    # Constructor
    def __init__(self, board, carDictionary):
        self.carDictionary = carDictionary
        self.board = board
        self.node_solution = None
        self.runtime = 0

    # Output all members
    def __str__(self):
        return f'Game: {self.board}'

    # If the puzzle contains AA then it is in goal state
    def is_goal_aa(self, board):
        goal_game = board[16:18]
        return goal_game == 'AA'



