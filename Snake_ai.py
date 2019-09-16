# import all the libraries
import random as rdm  # to generate random numbers
from tkinter import *  # for the display window
import time  # to wait some time when needed
import numpy as np  # to compute operations on arrays
import math  # for unlinear functions and infiny number
import pickle  # for saving and loading python objects
import sys  # to use interpreter arguments

# arguments initialisation
args = sys.argv
if len(args) > 3:
    raise IOError("You can only have two arguments! (nb_of_snakes (int), watch (bool))")
elif len(args) == 2:
    args.append(False)
elif len(args) == 1:
    args.append(500)
    args.append(False)
try:
    int(args[1])
    bool(args[2])
except:
    raise IOError("Incorrect arguments! (nb_of_snakes (int), watch (bool))")

# global variables
directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # the different possibilities of directions [N,S,W,E]
dimensions = (0, 20)  # the dimensions of the window (in decade of pixels)
maxsteps = 300  # how many steps they have at the beginning
save_path = time.strftime("saves/snake_%d.%m.%y_%Hh%Mmin%Ssec.pkl")  # the path where it saves the snake


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


class Population:
    """
    Population object.
    """

    def __init__(self, maxsteps, nb_of_snakes=int(args[1]), watch=bool(args[2])):
        """
        Initialisation method at the creation of a population.
        :param int maxsteps: how many steps the snakes in the population will have (maximum)
        :param int (even) nb_of_snakes: how many snakes are there in the population
        :param bool watch: if we want to watch the population of snakes learning (reducing a lot the performances) or not
        """
        if nb_of_snakes % 2:
            raise Exception("The number of snakes in the population has to be even.")
        self.pop = []  # the list of all the snakes in the population
        self.watch = watch  # if we want to watch the population learning
        self.maxsteps = maxsteps  # maximum of steps for each snake
        if self.watch:
            for i in range(nb_of_snakes):
                self.pop.append(Snake(maxsteps=maxsteps, display=True))
        else:
            for i in range(nb_of_snakes):
                self.pop.append(Snake(maxsteps=maxsteps))
        self.fitness_sum = 0  # the sum of all the snakes' fitness

    def move(self):
        """
        Moves all the snakes in the population.
        :return: None
        """
        for i in range(len(self.pop)):
            self.pop[i].move()  # mooves the snake
        if self.watch:
            self.show()  # shows the snake if needed

    def all_dead(self):
        """
        Returns True if all the snakes are dead.
        :return: bool res
        """
        res = 0  # how many snakes are dead
        for i in range(len(self.pop)):
            if self.pop[i].dead:
                res += 1
        return res == len(self.pop)

    def show(self):
        """
        Hides all dead snakes in the population.
        :return: None
        """
        for i in range(len(self.pop)):
            if self.pop[i].dead:
                self.pop[i].display_new = False
            self.pop[i].displayupdate()
        display.update()
        time.sleep(0.03)

    def calculfitness(self):
        """
        Calculates the fitness of each snake.
        :return: None
        """
        for i in range(len(self.pop)):
            self.pop[i].calculfitness()

    def fitness(self, e):
        """
        Returns the fitness of a given object (used to sort the snakes).
        :param e: Snake
        :return: float fitness
        """
        return e.fitness

    def crossover(self):
        """
        Mixing individuals in the population.
        :return: None
        """
        for i in range(int(len(self.pop) / 2)):
            for r in range(self.pop[2 * i].brain.w1.shape[0]):
                for c in range(self.pop[2 * i].brain.w1.shape[1]):
                    if rdm.randint(0, 1):
                        self.pop[2 * i].brain.w1[r][c], self.pop[2 * i + 1].brain.w1[r][c] = \
                            self.pop[2 * i + 1].brain.w1[r][c], self.pop[2 * i].brain.w1[r][c]
            for r in range(self.pop[2 * i].brain.w2.shape[0]):
                for c in range(self.pop[2 * i].brain.w2.shape[1]):
                    if rdm.randint(0, 1):
                        self.pop[2 * i].brain.w2[r][c], self.pop[2 * i + 1].brain.w2[r][c] = \
                            self.pop[2 * i + 1].brain.w2[r][c], self.pop[2 * i].brain.w2[r][c]
            for r in range(self.pop[2 * i].brain.w3.shape[0]):
                for c in range(self.pop[2 * i].brain.w3.shape[1]):
                    if rdm.randint(0, 1):
                        self.pop[2 * i].brain.w3[r][c], self.pop[2 * i + 1].brain.w3[r][c] = \
                            self.pop[2 * i + 1].brain.w3[r][c], self.pop[2 * i].brain.w3[r][c]

    def sumfitness(self):
        """
        Calculates the sum of all the snakes' fitness in the population.
        :return: None
        """
        self.fitness_sum = 0
        for i in range(len(self.pop)):
            self.fitness_sum += self.pop[i].fitness

    def naturalselection(self, maxsteps):
        """
        Generates a new population based on itself.
        :param int maxsteps: How many steps the old poppulation had
        :return: Population new_pop: The new population
        """
        self.calculfitness()
        self.sumfitness()
        self.pop.sort(key=self.fitness)  # sorts the snake by fitness
        self.pop[-1].save()  # saves the best snake
        overwatch(self.pop[-1])  # displays the best snake
        if pop.pop[-1].kb == "steps":
            maxsteps += 20
        new_pop = Population(maxsteps)  # creates a new population
        display.canv.itemconfig(display.maxsteps, text="Max steps: {}".format(maxsteps))
        for i in range(len(new_pop.pop)):
            individual = self.selectindividual()  # slections a snake
            new_pop.pop[i].brain.w1 = individual.brain.w1.copy()  # copies its neural network
            new_pop.pop[i].brain.w2 = individual.brain.w2.copy()
            new_pop.pop[i].brain.w3 = individual.brain.w3.copy()
        new_pop.crossover()  # mixes the snakes with each other
        for i in range(len(new_pop.pop)):
            new_pop.pop[i].brain.mutate()  # mutates all the snakes
        new_pop.pop[-1].brain.w1 = self.pop[-1].brain.w1.copy()  # inculdes the best snake of this population in the new one (without mutation)
        new_pop.pop[-1].brain.w2 = self.pop[-1].brain.w2.copy()
        new_pop.pop[-1].brain.w3 = self.pop[-1].brain.w3.copy()
        return new_pop

    def selectindividual(self):
        """
        Selects a snake in the population.
        :return: Snake
        """
        rand = rdm.uniform(0, self.fitness_sum)
        rsum = 0  # running sum
        for i in range(len(self.pop)):
            rsum += self.pop[i].fitness
            if rsum >= rand:
                return self.pop[i]

    def __del__(self):
        """
        Deletes all the snakes in the population.
        :return: None
        """
        for i in range(len(self.pop)):
            del self.pop[0]


class Square:
    """
    Square object.
    """

    def __init__(self, x, y, color):
        """
        Initialisation method at the creation of a square.
        :param int x: X coordinate
        :param int y: Y coordinate
        :param str color: the color of the square
        """
        self.show = display.canv.create_rectangle(10 * x + 5, 10 * y + 5, 10 * x + 10 + 5, 10 * y + 10 + 5, width=0,
                                                  fill=color)

    def __del__(self):
        """
        Deletes its display.
        :return:
        """
        try:
            display.canv.delete(self.show)
        except:
            pass


class Display:
    """
    Display object.
    """

    def __init__(self, title, size, gen, maxsteps):
        """
        Initialisation method at the creation of a display window.
        :param str title: Title of the window
        :param int size: Dimention of the playable area
        :param int gen: Starting generation
        :param int maxsteps: How many steps the snakes have at the beginning (maximum)
        """
        self.root = Tk()
        self.root.title(title)
        self.canv = Canvas(self.root, width=size + 6, height=size + 40)  # A bit higher to display informations
        self.canv.pack()
        # informations to display
        self.borders = self.canv.create_rectangle(10 * dimensions[0] + 4, 10 * dimensions[0] + 4,
                                                  10 * dimensions[1] + 5, 10 * dimensions[1] + 5, width=1, fill="white")
        self.gen = self.canv.create_text(5, size + 6, fill="darkblue", text="Gen: {}".format(gen), anchor="nw")
        self.maxsteps = self.canv.create_text(70, size + 6, fill="darkblue", text="Max steps: {}".format(maxsteps), anchor="nw")
        self.score = self.canv.create_text(5, size + 22, fill="darkblue", text="Score: [...]", anchor="nw")
        self.killedby = self.canv.create_text(70, size + 22, fill="darkblue", text="KB: [...]", anchor="nw")

    def update(self):
        """
        Updates the canvas.
        :return: None
        """
        self.canv.update()


def percentofzero(pop):
    """
    Prints the percentage of snakes who died without eating a fruit (in a given population).
    :param pop: Population
    :return: None
    """
    zero = 0
    for i in range(len(pop.pop)):
        if pop.pop[i].score == 0:
            zero += 1
    print(zero / len(pop.pop))


def sameid(pop):
    """
    Prints the percentage of snakes who have the exact same brain (in a given population).
    :param pop: Population
    :return: None
    """
    s = 0
    for i in range(len(pop.pop)):
        if pop.pop[i].brain.id == pop.pop[-1].brain.id:
            s += 1
    print(s / len(pop.pop))


def overwatch(snake):
    """
    Replays the game of a given snake.
    :param snake: Snake
    :return: None
    """
    display.canv.itemconfig(display.score, text="Score: {}".format(snake.score))  # displays it score
    display.canv.itemconfig(display.killedby, text="KB: {}".format(snake.kb))  # displays what killed it
    ow = Snake(maxsteps=snake.maxsteps, display=True, ow=True)  # creates a new snake
    ow.brain.w1 = snake.brain.w1.copy()  # copies its neural network
    ow.brain.w2 = snake.brain.w2.copy()
    ow.brain.w3 = snake.brain.w3.copy()
    ow.fruitslist = snake.fruitslist[:]  # copies its fruits list
    ow.fruit = ow.fruitslist[0]  # its first fruit
    ow.fruit.show = [Square(ow.fruit.pos[0], ow.fruit.pos[1], "green")]
    while not ow.dead:
        ow.move()
        ow.displayupdate()
        display.update()
        time.sleep(0.03)
    del ow
    display.canv.itemconfig(display.score, text="Score: [...]")
    display.canv.itemconfig(display.killedby, text="KB: [...]")


gen = 1 # the number of generations
display = Display("Snake AI", 10 * dimensions[1], gen, maxsteps)  # Creating the window
pop = Population(maxsteps)  # creates the first population
display.update()

while True:
    try:
        if not pop.all_dead():
            pop.move()
        else:
            new_pop = pop.naturalselection(pop.maxsteps)
            del pop
            gen += 1
            display.canv.itemconfig(display.gen, text="Gen: {}".format(gen))
            pop = new_pop
            display.update()
    except:
        del pop
        break