# import all the libraries 
import random as rdm  # to generate random numbers
from tkinter import *  # for graphics display in the window
import time  # to wait some time when needed

import keyboard  # to catch pressed key
import threading  # execute parallel loops

directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # the diffrent possibilities of directions
dimensions = (0, 20)  # the dimensions of the window

class Snake:
	"""
	Snake object.
	"""

	def __init__(self, hposx, hposy, length, direc, display):
		self.direc = directions[direc]  # its direction vector
		self.coords = []  # the list of all its points's coordinates
		self.show = []  # the list of its points in the canvas
		for i in range(length):
			self.coords.append((hposx, hposy - i))  # adding every coordinates to its list
		self.score = 0  # the number of fruit that it ate
		self.display = False  # if it is displayed or not
		self.displayNew = display  # if we want to hide or show it
		self.fruit = self.newFruit()  # its fruit
		self.step = 0
		self.displayUpdate()

	def displayUpdate(self):
		"""
		Checks if the displayNew is modified and make the required changes.
		"""
		if not self.display and self.displayNew:  # if we want to show it
			for i in self.coords:
				self.show.append(Square(i[0], i[1], "red"))
			self.fruit.show = Square(self.fruit.pos[0], self.fruit.pos[1], "green")
			self.display = True
		elif self.display and not self.displayNew:  # if we want to hide it
			for i in range(len(self.show)):
				del self.show[0]
			del self.fruit.show
			self.display = False

	def move(self):
		"""
		Moves the snake.
		"""
		self.step += 1
		self.newHead()
		self.check()
		self.displayUpdate()

	def changeDirec(self, newDirec):
		"""
		Changes the direction of the snake.
		"""
		if not directions[newDirec] == self.direc:
			self.direc = directions[newDirec]

	def newHead(self):
		"""
		Adds a new point towards the front of the snake.
		"""
		self.coords.insert(0, (self.coords[0][0] + self.direc[0], self.coords[0][1] + self.direc[1]))  # adding a new point depending on its acctual direction and its old head
		if self.display:
			self.show.insert(0, Square(self.coords[0][0], self.coords[0][1], "red"))  # adding the dispaly of this new point

	def shorten(self):
		"""
		Deletes the last point of the snake.
		"""
		del self.coords[len(self.coords) - 1]  # deleting the last point of its tale
		if self.display:
			del self.show[len(self.show) - 1]  # deleting the dispaly of the last point of its tale

	def check(self):
		"""
		Checks if it is going out of the window, touching its tale or eating the fruit.
		Shortens its tale otherwise.
		"""
		if self.coords[0][0] < dimensions[0] or self.coords[0][0] > dimensions[1] - 1 or self.coords[0][1] < dimensions[0] or self.coords[0][1] > dimensions[1] - 1:  # going out of the window
			end()
		elif self.coords.count(self.coords[0]) > 1:  # touching its tale
			end()
		elif self.coords[0][0] == self.fruit.pos[0] and self.coords[0][1] == self.fruit.pos[1]:  # eating the fruit
			self.score += 1
			del self.fruit
			self.fruit = self.newFruit()
		else:
			self.shorten()
		if self.step > 200:
			end()

	def newFruit(self):
		"""
		Generates a new fruit and returns it.
		"""
		fruit = Fruit()  # new fruit
		while (fruit.pos[0], fruit.pos[1]) in self.coords:  # executes while the fruit is in the snake
			fruit.pos = fruit.coordsFruit()
		if self.display == True:
			fruit.show = Square(fruit.pos[0], fruit.pos[1], "green")
		return fruit

	def __del__(self):
		"""
		Deletes its fruit and its display.
		"""
		try:
			for i in self.show:  # deletes its display
				del i
		except:
			pass
		del self.fruit

class Fruit:
	"""
	Fruit object.
	"""

	def __init__(self):
		self.pos = self.coordsFruit()  # its position
		self.show = None  # its display

	def coordsFruit(self):
		"""
		Returns a random postion in the window.
		"""
		return [rdm.randint(dimensions[0], dimensions[1] - 1), rdm.randint(dimensions[0], dimensions[1] - 1)]

	def __del__(self):
		"""
		Deletes its display.
		"""
		try:
			del self.show
		except AttributeError:
			pass

class Display:
	"""
	Display object.
	"""

	def __init__(self, title, size):
		self.root = Tk()
		self.root.title(title)
		self.canv = Canvas(self.root, width=size + 6, height=size + 30)
		self.canv.pack()
		self.borders = self.canv.create_rectangle(10 * dimensions[0] + 4, 10 * dimensions[0] + 4, 10 * dimensions[1] + 5, 10 * dimensions[1] + 5, width=1, fill="white")
		self.score = self.canv.create_text(5, size + 5, fill="darkblue", text="Score: ", anchor="nw")

	def update(self):
		"""
		Updating the canvas and the displayed texts.
		"""
		self.canv.update()
		display.canv.itemconfig(display.score, text="Score: {}".format(snake.score))

class Square:
	"""
	Square object.
	"""

	def __init__(self, x, y, color):
		self.show = display.canv.create_rectangle(10 * x + 5, 10 * y + 5, 10 * x + 10 + 5, 10 * y + 10 + 5, width=0, fill=color)

	def __del__(self):
		"""
		Deletes its display.
		"""
		try:
			display.canv.delete(self.show)
		except:
			pass

def end():
	"""
	Ends the game and restarts another one.
	"""
	global snake
	del snake
	snake = Snake(4, 4, 4, 0, True)

def keyboardwait():
	"""
	Catches user's keyboard inputs.
	"""
	while user:
		if keyboard.is_pressed('Right'):
			try:
				snake.changeDirec(2)
			except:
				pass
		elif keyboard.is_pressed('Up'):
			try:
				snake.changeDirec(1)
			except:
				pass
		elif keyboard.is_pressed('Down'):
			try:
				snake.changeDirec(0)
			except:
				pass
		elif keyboard.is_pressed('Left'):
			try:
				snake.changeDirec(3)
			except:
				pass
		elif keyboard.is_pressed('o'):
			try:
				snake.displayNew = True
			except:
				pass
		elif keyboard.is_pressed('i'):
			try:
				snake.displayNew = False
			except:
				pass

user = True  # to begin the keyboard loop

display = Display("Snake", 10 * dimensions[1])  # Creating the window
snake = Snake(4, 4, 4, 0, True)  # Creating the snake

display.update()

threading.Thread(None, target=keyboardwait).start()  # executing keyboardwait in parallel

while True:
	try:
		snake.move()
		display.update()
	except:
		del snake
		user = False  # to end the keyboard loop
		break
	time.sleep(0.15)  # wait a bit to let the user play
