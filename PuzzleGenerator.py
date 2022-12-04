import math
import random
import copy


# Function for drawing a car on a given grid
def drawCar(grid, name, length, direction, row, column):
    # working on a copy of the grid
    newGrid = copy.copy(grid)

    # finding the row on which AA car is placed
    for i in range(len(grid)):
        if 'AA' in grid[i]:
            red_row = i

    if direction == 'h' and column != len(grid) - 1:

        distanceToBorder = length if length <= len(grid) - column else len(grid) - column

        drew = 0

        # in case the horizontal car is in front of Target car -> avoid placing it in the exit(3f) position
        if row == red_row and distanceToBorder > 1:
            distanceToBorder = distanceToBorder - 1

        # drawing the car on the grid
        for i in range(distanceToBorder):
            if column < len(grid) and newGrid[row][column] == '.':
                newGrid[row] = newGrid[row][:column] + name + newGrid[row][column + 1:]
                drew += 1
                column += 1

        # If it can't draw a car with length of at least two -> return original grid
        if drew < 2:
            return grid
        else:
            return newGrid

    elif direction == 'v' and row != len(grid) - 1:

        distanceToBorder = length if length <= len(grid) - row else len(grid) - row

        drew = 0

        for i in range(distanceToBorder):
            if row < len(grid) and newGrid[row][column] == '.':
                newGrid[row] = newGrid[row][:column] + name + newGrid[row][column + 1:]
                drew += 1
                row += 1

        # If it can't draw a car with length of at least two -> return original grid
        if drew < 2:
            return grid
        else:
            return newGrid

    else:
        return grid


# Function to generate a board/puzzle
def generateBoard(boardSize):
    # the size of column/row of the board
    n = int(math.sqrt(boardSize))

    # the grid
    grid = []

    # creating the empty grid
    for i in range(n):
        mystr = ''
        for j in range(n):
            mystr = mystr + '.'
        grid.append(mystr)

    # Indicating the row on which the ambulance (red car) should be placed
    red_row = 0

    if n % 2 == 0:
        red_row = int(n / 2 - 1)
    else:
        red_row = int(n / 2)

    # choosing its column by random - to make puzzle more difficult we put AA either at 1st or 2nd column
    red_column = int(random.randrange(0, 2))

    # Placing the Ambulance 'AA' car first -> at the red_row and red_column
    grid[red_row] = grid[red_row][:red_column] + 'AA' + grid[red_row][red_column + 2:]

    # The maximum number of cars the puzzle can have is
    #  when all cars are size 2 ( excluding the red car, and keeping at least one position empty)
    maxCarNumber = 0

    if boardSize % 2 == 0:
        maxCarNumber = boardSize / 2 - 2
    else:
        maxCarNumber = int(boardSize / 2) - 1

    # Choosing the number of cars to be created
    carNumber = int(random.randrange(5, maxCarNumber + 1))

    # The list of all possible car names
    carNames = []

    # Creating the list of possible car names
    for i in range(ord('B'), ord('Z')):
        carNames.append(chr(i))

    # possible directions for each car -> 'v' as vertical and 'h' as horizontal
    directions = ['v', 'h']

    # Drawing each car
    for i in range(1, carNumber):

        # randomly choosing the name of the car
        name = random.choice(carNames)

        # removing that name from the list of all possible names for the cars
        carNames.remove(name)

        # choosing the length of the car randomly
        # The possible length of each car is between 2 and half of the row/column of the puzzle
        carLength = int(random.randrange(2, n / 2 + 1))

        # choosing the direction of the car randomly
        carDirection = random.choice(directions)

        # choosing an empty position
        carRow = int(random.randrange(0, n))
        carColumn = int(random.randrange(0, n))

        # Making sure an empty position is chosen
        while grid[carRow][carColumn] != '.':
            carRow = int(random.randrange(0, n))
            carColumn = int(random.randrange(0, n))

        # Drawing the car
        grid = drawCar(grid, name, carLength, carDirection, carRow, carColumn)




    # Formatting the grid as a string
    board = ''
    for row in grid:
        board += row

    # Choosing by random whether to creat a fuel list for the puzzle -> 1 means 'yes' and 0 means 'no'
    toCreateFuelList = int(random.choice([0, 1]))

    # Creating a fuel list for each puzzle
    if toCreateFuelList:

        # Variable to save the name of all cars of the board
        cars = []

        # Getting the name of all the cars in the board/puzzle
        for car in board:
            if car != '.' and car not in cars:
                cars.append(car)

        # Randomly choosing the number of cars for which the fuel is to be set
        carNum_toFuel = int(random.randrange(1, len(cars) + 1))

        # The cars for which the fuel is to be set
        carsToFuel = []

        # Choosing the cars for which the fuel is to be set
        for i in range(1, carNum_toFuel):
            choice = random.choice(cars)

            if choice not in carsToFuel:
                carsToFuel.append(choice)

        # Adding the fuel list to the end of the board
        for i in range(len(carsToFuel)):
            board += ' '
            board += carsToFuel[i]
            board += '{:0>2}'.format(random.randrange(1, 100))

    return board


# Function to create a number of puzzles of a given size
def creatPuzzles( puzzleNum, board_size):
    # Checking if the file is already generated
    try:
        # creating the file for saving the generating puzzles
        f = open('input/generatedPuzzles.txt', 'x')

        # generating "puzzleNum" number of puzzles
        for i in range(puzzleNum):
            # saving the puzzle number
            f.write("# Puzzle ")
            f.write(str(i + 1))
            f.write('\n')
            # generating a puzzle
            f.write(generateBoard(board_size))
            f.write('\n\n')

        f.close()
    # If the file already exists then we skip regenerating puzzles to save time
    except:
        print(" Puzzles are already generated")


#--------------------------------------------------------------------------------------------
# USe the following code in the main file to create 50 puzzles that are of size 6x6 (size 36)
#creatPuzzles(50,36)
#---------------------------------------------------------------------------------------------
