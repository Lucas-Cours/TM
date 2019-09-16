# import all the libraries
import random as rdm  # to generate random numbers
from tkinter import *  # for the display window
import time  # to wait some time when needed
import numpy as np  # to compute operations on arrays
import math  # for unlinear functions and infiny number
import pickle  # for saving and loading python objects
import sys  # to use interpreter arguments
import glob  # to use saved files
import os  # to use saved files

directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # the different possibilities of directions
dimensions = (0, 20)  # the dimensions of the window


def choosefile(path=""):
    """
    Asks the user the path and takes out the snake of the file.
    :param str path: Path to the snake file
    :return: Snake
    """
    try:
        if path == "":
            name = input(
                "Type the name of the snake's file that you want to load or type 'last' if you want to load the last played snake: ")
        else:
            name = path
        if name == "last":
            list_of_files = glob.glob('saves/*')
            name = max(list_of_files, key=os.path.getctime)
            file = open(name, "rb")
        else:
            file = open("saves/" + name, "rb")
        return pickle.load(file)
    except:
        print("This file is incorrect. Try again.")
        return choosefile()


def choose():
    """
    Asks the user if he wants to load or play the snake.
    :return: str
    """
    what = input("Type 'load' if you want to rewatch the exact same game or type 'play' if you want to watch the snake play with random fruits: ")
    if what == "load" or what == "play":
        return what
    else:
        print("You have to type 'load' or 'play'. Try again.")
        return choose()


class Snake:
    """
    Snake object.
    """

    def __init__(self, hposx=int(dimensions[1]/2), hposy=int(dimensions[1]/2), length=4, direc=3, display=False, maxsteps=300, ow=False):
        """
        Initialisation method at the creation of a snake.
        :param int hposx: starting position of the snake on the X axis
        :param int hposy: starting position of the snake on the Y axis
        :param int length: the starting length of the snake
        :param int (between 0 and 3) direc: the starting direction the snake is facing
        :param bool display: if we want it to be displayed in the window or not
        :param int maxsteps: how many steps it has (maximum)
        :param bool ow: if it is an overwatch snake or not
        """
        if direc not in [0, 1, 2, 3]:
            raise Exception("The starting direction of the snake has to be 0, 1, 2 or 3 (N, S, W, E).")
        self.direc = directions[direc]  # its direction vector
        self.coords = []  # the list of all its points' coordinates
        self.show = []  # the list of its points in the canvas
        for i in range(length):
            self.coords.append(
                (hposx - i * self.direc[0], hposy - i * self.direc[1]))  # adds every coordinate to its list
        self.score = 0  # the number of fruits that it ate
        self.display = False  # if it is displayed or not
        self.display_new = display  # if we want to hide or show it
        self.fruit = self.newfruit()  # its fruit
        self.fruitslist = [self.fruit]  # all its fruits
        self.fruit_index = 1  # which fruit will be the next in the list
        self.ow = ow  # if it is an overwath snake
        self.brain = Brain(13)  # its brain
        self.dead = False  # if it is dead
        self.step = 0  # how many steps it has done yet
        self.maxsteps = maxsteps  # how many steps it has at disposal
        self.fitness = 0  # how good it is
        self.kb = None  # what killed it
        self.displayupdate()

    def displayupdate(self):
        """
        Checks if the display_new is modified and makes the required changes.
        :return: None
        """
        if not self.display and self.display_new:  # if we want to show it
            for i in self.coords:
                self.show.append(Square(i[0], i[1], "red"))
            self.fruit.show = [Square(self.fruit.pos[0], self.fruit.pos[1], "green")]
            self.display = True
        elif self.display and not self.display_new:  # if we want to hide it
            for i in range(len(self.show)):
                del self.show[0]
            del self.fruit.show[0]
            self.display = False

    def move(self):
        """
        Moves the snake.
        :return: None
        """
        if not self.dead:
            self.step += 1
            self.changedirec(self.brain.output(self.calculinputs()))  # asks the brain to return a value based on its input
            self.check()

    def changedirec(self, new_direc):
        """
        Changes the direction of the snake.
        :param int (between 0 and 3) new_direc: the new directions the snake will be facing
        :return: None
        """
        if not directions[new_direc] == self.direc and not directions[new_direc] == (-self.direc[0], -self.direc[1]):
            self.direc = directions[new_direc]

    def newhead(self):
        """
        Adds a new point towards the front of the snake.
        :return: None
        """
        self.coords.insert(0, (self.coords[0][0] + self.direc[0], self.coords[0][1] + self.direc[
            1]))  # adds a new point depending on its acctual direction and its old head
        if self.display:
            self.show.insert(0, Square(self.coords[0][0], self.coords[0][1],
                                       "red"))  # adds the dispaly of this new point if needed

    def shorten(self):
        """
        Deletes the last point of the snake.
        :return: None
        """
        del self.coords[len(self.coords) - 1]  # delets the last point of its tail
        if self.display:
            del self.show[len(self.show) - 1]  # delets the dispaly of the last point of its tail if needed

    def check(self):
        """
        Checks if it is going out of the window, touching its tail or eating the fruit.
        Shortens its tail otherwise.
        :return: None
        """
        newhead = (self.coords[0][0] + self.direc[0], self.coords[0][1] + self.direc[1])
        if newhead[0] < dimensions[0] or newhead[0] > dimensions[1] - 1 or newhead[1] < dimensions[0] or newhead[1] > \
                dimensions[1] - 1:  # goes out of the window
            self.kb = "wall"
            self.dead = True
        elif self.coords.count(newhead) == 1:  # touchs its tail
            self.kb = "tail"
            self.dead = True
        elif self.coords[0][0] == self.fruit.pos[0] and self.coords[0][1] == self.fruit.pos[1]:  # eats the fruit
            self.newhead()
            self.score += 1
            if not self.ow:
                self.fruit.__del__()
                self.fruit = self.newfruit()
                self.fruitslist.append(self.fruit)
            else:
                self.fruitslist[self.fruit_index - 1].__del__()
                try:
                    self.fruit = self.fruitslist[self.fruit_index]
                except:
                    print(self.step, "of", self.maxsteps)
                self.fruit.show = [Square(self.fruit.pos[0], self.fruit.pos[1], "green")]
                self.fruit_index += 1
        else:
            self.newhead()
            self.shorten()
        if self.step == self.maxsteps:  # reaches the maximum of steps
            self.kb = "steps"
            self.dead = True

    def newfruit(self):
        """
        Generates a new fruit and returns it
        :return: Fruit fruit: the new fruit
        """
        fruit = Fruit()  # creates a new fruit
        while (fruit.pos[0], fruit.pos[1]) in self.coords:  # executes while the fruit is in the snake body
            fruit.pos = fruit.coordsfruit()
        if self.display:
            fruit.show = [Square(fruit.pos[0], fruit.pos[1], "green")]  # displays the new fruit if needed
        return fruit

    def calculinputs(self):
        """
        Calculates all the snake's inputs.
        :return: np.ndarray inputs: two-dimensional array wich contains all the inputs + a bias
        """
        eyes_w = [0, 0, 0, 0]  # its vision till a wall (N, S, W, E)
        eyes_t = [0, 0, 0, 0]  # its vision till its tail
        eyes_f = [0, 0, 0, 0]  # its vision till the fruit
        eyes_w[0] = 1 / (self.coords[0][1] - dimensions[0] + 1)  # North wall
        eyes_w[1] = 1 / (dimensions[1] - self.coords[0][1])   # South wall
        eyes_w[2] = 1 / (self.coords[0][0] - dimensions[0] + 1)  # West wall
        eyes_w[3] = 1 / (dimensions[1] - self.coords[0][0])  # East wall
        for i in range(dimensions[1]):  # North tale
            if (self.coords[0][0], self.coords[0][1] - i - 1) in self.coords:
                eyes_t[0] = 1 / (i + 1)
                break
        for i in range(dimensions[1]):  # South tale
            if (self.coords[0][0], self.coords[0][1] + i + 1) in self.coords:
                eyes_t[1] = 1 / (i + 1)
                break
        for i in range(dimensions[1]):  # West tale
            if (self.coords[0][0] - i - 1, self.coords[0][1]) in self.coords:
                eyes_t[2] = 1 / (i + 1)
            break
        for i in range(dimensions[1]):  # East tale
            if (self.coords[0][0] + i + 1, self.coords[0][1]) in self.coords:
                eyes_t[3] = 1 / (i + 1)
                break
        if self.fruit.pos[0] == self.coords[0][0]:  # North or South fruit
            dist = self.coords[0][1] - self.fruit.pos[1]
            if dist > 0:
                eyes_f[0] = dist
            else:
                eyes_f[1] = - dist
        elif self.fruit.pos[1] == self.coords[0][1]:  # West or East tale
            dist = self.coords[0][0] - self.fruit.pos[0]
            if dist > 0:
                eyes_f[2] = dist
            else:
                eyes_f[3] = - dist
        inputs = np.array([[
                eyes_w[0], eyes_w[1], eyes_w[2], eyes_w[3],
                eyes_t[0], eyes_t[1], eyes_t[2], eyes_t[3],
                eyes_f[0], eyes_f[1], eyes_f[2], eyes_f[3], 1  # bias
        ]])
        return inputs

    def calculfitness(self):
        """
        Calculates the fitness of the snake.
        :return: None
        """
        self.fitness = (self.score**2)*(1 + (self.score/math.sqrt(self.step) + 1)**3)

    def save(self):
        """
        Saves the snake with pickle.
        :return: None
        """
        pickle.dump(self, open(save_path, 'wb'))

    def __del__(self):
        """
        Deletes its fruit and its display.
        :return: None
        """
        try:
            for i in range(len(self.show)):  # deletes its display
                del self.show
        except:
            pass
        del self.fruit


class Fruit:
    """
    Fruit object.
    """

    def __init__(self):
        """
        Initialisation method at the creation of a fruit.
        """
        self.pos = self.coordsfruit()  # its position
        self.show = []  # its display

    def coordsfruit(self):
        """
        Randomize a position in the window.
        :return: list: a random postion in the window
        """
        return [rdm.randint(dimensions[0], dimensions[1] - 1), rdm.randint(dimensions[0], dimensions[1] - 1)]

    def __del__(self):
        """
        Deletes its display.
        :return: None
        """
        try:
            del self.show[0]
        except:
            pass


class Brain:
    """
    Brain object.
    """

    def __init__(self, nb_of_inputs):
        """
        Initialisation method at the creation of a fruit.
        :param int nb_of_inputs: the number of different inputs in the array given by the calculinputs method
        """
        self.w1 = np.random.uniform(-1, 1, (nb_of_inputs, 10))  # the first neurons layer
        self.w2 = np.random.uniform(-1, 1, (10, 8))  # the second neurons layer
        self.w3 = np.random.uniform(-1, 1, (8, 4))  # the third neurons layer
        self.mutation_chance = 0.01  # the mutation probability
        self.id = rdm.uniform(0, 1)  # its unique id

    def tanh(self, x):
        """
        Hyperbolic tangent function.
        :param x: float
        :return: float
        """
        return math.tanh(x)

    def sigmoid(self, x):
        """
        Sigmoid function.
        :param x: float
        :return: float
        """
        return 1 / (1 + math.exp(-x))

    def output(self, data):
        """
        Calculates the neural network output using matrix calculation and the different weights of the arrays.
        :param np.ndarray data: the input array
        :return: int: the index of the maximum value in the output array
        """
        h1 = np.dot(data, self.w1)  # matrix dot product
        for c in range(h1.shape[1]):
            h1.itemset(c, self.tanh(h1.item(c)))  # unlinear function
        h2 = np.dot(h1, self.w2)  # matrix dot product
        for c in range(h2.shape[1]):
            h2.itemset(c, self.tanh(h2.item(c)))  # unlinear function
        output = np.dot(h2, self.w3)  # matrix dot product
        for c in range(output.shape[1]):
            output.itemset(c, self.tanh(output.item(c)))  # unlinear function
        return self.max(output)

    def max(self, array):
        """
        Calculates the maximum value of a given array.
        :param np.ndarray array: a full array
        :return: int index: the index of the maximum value in the array
        """
        index = 0
        for i in range(array.size):
            if array[0][i] > array[0][index]:
                index = i
        return index

    def arraymutate(self, array):
        """
        Potentially (depending on the rate: self.mutation_chance) mutates a given array and modifies the brain id if a mutation took place.
        :param np.ndarray array: a full array
        :return: np.ndarray array: the potentially modified array
        """
        mut = False
        for r in range(array.shape[0]):
            for c in range(array.shape[1]):
                x = rdm.uniform(0, 1)
                if x < self.mutation_chance:  # if the random number is bigger than the rate => mutation
                    array[r][c] = rdm.uniform(-1, 1)  # mutates the weight
                    mut = True
        if mut:
            self.id = rdm.uniform(0, 1)  # new unique id
        return array

    def mutate(self):
        """
        Applies the arraymutate method to all the weights of the arrays.
        :return: None
        """
        self.w1 = self.arraymutate(self.w1)
        self.w2 = self.arraymutate(self.w2)
        self.w3 = self.arraymutate(self.w3)


class Square:
    """
    Square object.
    """

    def __init__(self, x, y, color):
        """
        Initialisation.
        """
        self.show = display.canv.create_rectangle(10 * x + 5, 10 * y + 5, 10 * x + 10 + 5, 10 * y + 10 + 5, width=0,
                                                  fill=color)

    def __del__(self):
        """
        Deletes its display.
        """
        try:
            display.canv.delete(self.show)
        except:
            pass


class Display:
    """
    Display object.
    """

    def __init__(self, title, size):
        """
        Initialisation method at the creation of a display window.
        :param str title: Title of the window
        :param int size: Dimention of the playable area
        """
        self.root = Tk()
        self.root.title(title)
        self.canv = Canvas(self.root, width=size + 6, height=size + 40)
        self.canv.pack()
        self.borders = self.canv.create_rectangle(10 * dimensions[0] + 4, 10 * dimensions[0] + 4,
                                                  10 * dimensions[1] + 5, 10 * dimensions[1] + 5, width=1, fill="white")
        if do == "load":
            self.maxsteps = self.canv.create_text(5, size + 6, fill="darkblue", text="Max steps: {}".format(base_snake.maxsteps), anchor="nw")
            self.score = self.canv.create_text(5, size + 22, fill="darkblue", text="Score: {}".format(base_snake.score), anchor="nw")
            self.killedby = self.canv.create_text(70, size + 22, fill="darkblue", text="KB: {}".format(base_snake.kb), anchor="nw")
        if do == "play":
            self.score = self.canv.create_text(5, size + 6, fill="darkblue", text="Score: 0", anchor="nw")

    def update(self):
        """
        Updating the canvas and the displayed texts.
        :return: None
        """
        if do == "play":
            display.canv.itemconfig(display.score, text="Score: {}".format(snake.score))
        self.canv.update()

# arguments initialisation
args = sys.argv
do = None
base_snake = None
if len(args) > 3:
    raise IOError("You can only have two arguments! ('load' or 'play' (str), file (str))")
elif len(args) == 2:
    do = ''.join(args[1])
    if do != 'play' and do != 'load':
        raise IOError("Incorrect arguments! ('load' or 'play' (str), file (str))")
    base_snake = choosefile()
elif len(args) == 3:
    do = ''.join(args[1])
    base_snake = choosefile(path=''.join(args[2]))
    if do != "play" and do != "load":
        raise IOError("Incorrect arguments! ('load' or 'play' (str), file (str))")
elif len(args) == 1:
    args.append(choose())
    args.append(choosefile())
    do = args[1]
    base_snake = args[2]

display = Display("Snake Replay", 10 * dimensions[1])

if do == "load":
    snake = Snake(maxsteps=base_snake.maxsteps, display=True, ow=True)
    snake.brain.w1 = base_snake.brain.w1.copy()  # copies its neural network
    snake.brain.w2 = base_snake.brain.w2.copy()
    snake.brain.w3 = base_snake.brain.w3.copy()
    snake.fruitslist = base_snake.fruitslist[:]  # copies its fruits list
    snake.fruit = snake.fruitslist[0]
    snake.fruit.show = [Square(snake.fruit.pos[0], snake.fruit.pos[1], "green")]
    display.update()
    time.sleep(0.03)
    try:
        while not snake.dead:
            snake.move()
            snake.displayupdate()
            display.update()
            time.sleep(0.03)
        del snake
    except:
        pass

elif do == "play":
    snake = Snake(maxsteps=math.inf, display=True)
    snake.brain.w1 = base_snake.brain.w1.copy()  # copies its neural network
    snake.brain.w2 = base_snake.brain.w2.copy()
    snake.brain.w3 = base_snake.brain.w3.copy()
    display.update()
    time.sleep(0.03)
    try:
        while True:
            if not snake.dead:
                snake.move()
                display.update()
                time.sleep(0.03)
            else:
                new = Snake(maxsteps=math.inf, display=True)
                new.brain.w1 = base_snake.brain.w1.copy()
                new.brain.w2 = base_snake.brain.w2.copy()
                new.brain.w3 = base_snake.brain.w3.copy()
                del snake
                snake = new
    except:
        pass

print("FINISHED !")
