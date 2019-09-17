#import all the libraries
from tkinter import *	#for the window
import math				#for the number pi
import random			#for generating random numbers
import time				#for waiting a bit

#canva functions
def canv_elipse_create(x,y,color):
	""" Showing a circle with a color. (x and y are the center of it) """
	return canv.create_oval(x-3, y-3, x+3, y+3, width = 0, fill = color)

def canv_texte_create(x,y,text):
	""" Showing a text. """
	return canv.create_text(x,y,fill="darkblue", text=text)

def canv_texte_modify(name, text):
	""" Modify the text in the window. """
	canv.itemconfig(name, text = text)

def canv_elipse_modify(name,x,y):
	""" Modify the coords of a point in the window."""
	canv.coords(name,x-3,y-3,x+3,y+3)

#vectors functions
def vector(x,y):
	""" Return a list of two components. """
	return [x,y]

def distance(pos,x,y):
	""" Return the distance between two points. """
	vect = vector(x - pos[0], y - pos[1])
	norme_vect = (vect[0]**2 + vect[1]**2)**0.5
	return norme_vect

def limit(vector,maxi):
	""" Limit each component from a vector by a given value called maxi. """
	if vector[0] > maxi:
		vector[0] = maxi
	if vector[1] > maxi:
		vector[1] = maxi
	if vector[0] < -maxi:
		vector[0] = -maxi
	if vector[1] < -maxi:
		vector[1] = -maxi

#generation function
def gen():
	""" Increase the generation number by one and update the text. """
	global generation
	generation += 1
	canv_texte_modify(show_gen, "Gen: " + str(generation))

#Dot object
class Dot:

	def __init__(self):
		self.pos = vector(300,550)	#pops up at the bottom of the window
		self.vel = vector(0,0)		#starts velocity = 0
		self.acc = vector(0,0)		#starts acceleration = 0
		self.brain = Brain(600)		#has a brain containing 400 acceleration vectors
		self.canv = canv_elipse_create(self.pos[0], self.pos[1],'black')	#shows it on the window
		self.dead = False	#turns to True if it dies
		self.reachgoal = False	#turns to True if it reaches the goal
		self.isbest = False		#turns to True if it is the best of the generation
		self.fitness = 0	#how good it is (how far he is from the goal)

	def __del__(self):
		try:
			canv.delete(self.canv)	#disappears from the window when deleted
		except:
			pass

	def show(self):
		""" Update its position in the window. """
		canv_elipse_modify(self.canv,self.pos[0], self.pos[1])

	def move(self):
		""" Update its position. """
		if self.dead == False and self.reachgoal == False:	#if not dead and not reached the goal
			if len(self.brain.directions) > self.brain.step:	#if there are still acceleration vectors
				self.acc = self.brain.directions[self.brain.step]
				self.brain.step += 1
				self.vel = [self.vel[0] + self.acc[0], self.vel[1] + self.acc[1]]	# add the acceleration to the velocity
				limit(self.vel,4)	#limit the velocity
				self.pos = [self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]]	# add the velocity to the position
			else:
				self.dead = True
			if self.pos[0] > 598 or self.pos[1] > 598 or self.pos[0] < 4 or self.pos[1] < 4:	#if it tries to go out of the window
				self.dead = True
			if self.pos[0] >= goal_pos[0][0] and self.pos[0] <= goal_pos[1][0] and self.pos[1] >= goal_pos[0][1] and self.pos[1] <= goal_pos[1][1]:		#if it touched the goal
				self.reachgoal = True
			if self.pos[0] >= obstacle_pos[0][0] and self.pos[0] <= obstacle_pos[1][0] and self.pos[1] >= obstacle_pos[0][1] and self.pos[1] <= obstacle_pos[1][1]:		#if it hits an obstacle
				self.dead = True
			#if self.pos[0] >= obstacle2_pos[0][0] and self.pos[0] <= obstacle2_pos[1][0] and self.pos[1] >= obstacle2_pos[0][1] and self.pos[1] <= obstacle2_pos[1][1]:		#if it hits an obstacle
			#	self.dead = True
			#if self.pos[0] >= obstacle3_pos[0][0] and self.pos[0] <= obstacle3_pos[1][0] and self.pos[1] >= obstacle3_pos[0][1] and self.pos[1] <= obstacle3_pos[1][1]:		#if it hits an obstacle
			#	self.dead = True

	def calcul_fitness(self):
		""" Calculate how good it is. """
		if self.reachgoal == True:	#if it reached the goal
			self.fitness = 9/9 + 20/self.brain.step
		else:	#else the fitness is 1/distance to the goal
			self.fitness = 9/distance(self.pos,300,20)

	def clone(self):
		""" Return a child dot with the same brain as the current dot. """
		cloned = Dot()
		cloned.brain.directions = self.brain.directions
		return cloned

#Brain object
class Brain:

	def __init__(self,size):
		self.size = size	#the amount of vectors in the directions list
		self.directions = []	#the list which contains all the acceleration vectors
		self.step = 0	#where we are in the list
		self.randomize()	#at its creation randomize all the vectors in the list
	
	def randomize(self):
		""" For each element of the list randomize a vector. """
		for i in range(self.size):
			random_angle = random.uniform(0,2*math.pi)	#generate a random angle
			self.directions.append([math.cos(random_angle),math.sin(random_angle)])	#take the vector from this angle

	def mutate(self):
		""" Randomize several vectors in the list. """
		mutation_chance = 0.03
		new_directions = []
		for i in range(self.size):	#randomize all the vectors in the new list
			random_angle = random.uniform(0,2*math.pi)
			new_directions.append([math.cos(random_angle),math.sin(random_angle)])
		for i in range(self.size):
			r = random.uniform(0,1)
			if r > mutation_chance:
				new_directions[i] = self.directions[i]	#put the same vector from the old list into the new list if the mutation chance wasn't big enough
		return new_directions

#Population object
class Population():

	def __init__(self,nb_of_dots):
		""" Create a population of dots. """
		self.nb_of_dots = nb_of_dots
		self.dots_list = []
		for i in range(nb_of_dots):
			self.dots_list.append(Dot())
		self.fitness_sum = 0

	def show(self):
		""" Show all the dots in the window. """
		for i in range(len(self.dots_list)):
			self.dots_list[i].show()

	def move(self):
		""" Move all the dots. """
		for i in range(len(self.dots_list)):	
			self.dots_list[i].move()

	def all_dead(self):
		""" Return True if all the dots are dead. """
		res = 0
		for i in range(len(self.dots_list)):
			if self.dots_list[i].dead == True:
				res += 1
			if self.dots_list[i].reachgoal == True:
				if self.dots_list[i].isbest == False:
					res	+= 1
				else:
					res = len(self.dots_list)
		return res == len(self.dots_list)

	def calcul_fitness(self):
		""" Calculate the fitness of all the dots. """
		for i in range(len(self.dots_list)):
			self.dots_list[i].calcul_fitness()

	def sum_fitness(self):
		""" Calculate the sum of the fitnesses of all the dots. """
		self.fitness_sum = 0
		for i in range(len(self.dots_list)):
			self.fitness_sum += self.dots_list[i].fitness

	def natural_selection(self):
		""" Select the dots for the next generation. """
		newpop = Population(self.nb_of_dots)
		self.best_dot()
		for i in range(len(self.dots_list) - 1):
				individual = self.select_individual()
				newpop.dots_list[i] = individual.clone()
		newpop.dots_list[len(self.dots_list) - 1] = self.dots_list[len(self.dots_list) - 1].clone()	#the last dot in the newpop list is the best of the previous generation
		newpop.dots_list[len(self.dots_list) - 1].isbest = True
		canv.itemconfig(newpop.dots_list[len(self.dots_list) - 1].canv, fill="green") #it shows it as green
		return newpop

	def select_individual(self):
		""" Select a dot in the dots list. """
		rand = random.uniform(0,self.fitness_sum)
		rsum = 0
		for i in range(len(self.dots_list)):	#if a dot has a high fitness it has more chance to get chosen
			rsum += self.dots_list[i].fitness
			if rsum >= rand:
				return self.dots_list[i]

	def best_dot(self):
		""" Sort the dots list and find the best dot and show its step if it reached the goal. """
		self.sum_fitness()
		self.dots_list.sort(key = self.return_fitness)		#sort the list (from the lowest fitness first to the highest at the end)
		if self.dots_list[len(self.dots_list) - 1].reachgoal == True:
			canv_texte_modify(show_steps, "Steps: " + str(self.dots_list[len(self.dots_list) - 1].brain.step))

	def return_fitness(self, e):
		""" Just return the fitness of a dot. (Used to sort the list) """
		return e.fitness

	def mutate(self):
		""" Mutate all the dots except the best one. """
		for i in range(len(self.dots_list)):
			if self.dots_list[i].isbest == False:
				self.dots_list[i].brain.directions = self.dots_list[i].brain.mutate()

	def __del__(self):
		""" Delete all the dots. """
		for i in range(len(self.dots_list)):
			del self.dots_list[0]


############
#   MAIN   #
############

#initialisation of the window
root = Tk()
root.title("Dot Ai")
canv = Canvas(root, width=600, height=600)	#window dimensions
canv.pack()
frame_rate = 0.01

#initialisation of the goal and the obstacles
goal_pos = [(290,10),(310,30)]
obstacle_pos = [(0,230),(450,250)]
#obstacle_pos = [(0,190),(450,210)]
#obstacle2_pos = [(150,320),(600,340)]
#obstacle3_pos = [(0,450),(450,470)]
canv.create_rectangle(goal_pos[0][0], goal_pos[0][1], goal_pos[1][0], goal_pos[1][1], width = 0, fill = 'red')
canv.create_rectangle(obstacle_pos[0][0], obstacle_pos[0][1], obstacle_pos[1][0], obstacle_pos[1][1], width = 0, fill = 'blue')
#canv.create_rectangle(obstacle2_pos[0][0], obstacle2_pos[0][1], obstacle2_pos[1][0], obstacle2_pos[1][1], width = 0, fill = 'blue')
#canv.create_rectangle(obstacle3_pos[0][0], obstacle3_pos[0][1], obstacle3_pos[1][0], obstacle3_pos[1][1], width = 0, fill = 'blue')

#intialisation of the texts in the window
generation = 1
show_gen = canv_texte_create(30,8,"Gen: " + str(generation))
show_steps = canv_texte_create(30,22,"Steps: ")

#create first population
pop = Population(100)
pop.show()

#the loop
while True:
	if pop.all_dead() == False:
		pop.move()
		pop.show()
	else:
		pop.calcul_fitness()
		newpop = pop.natural_selection()
		newpop.mutate()
		del pop
		pop = newpop
		gen()
	try:
		canv.update()
	except:
		pass
	time.sleep(frame_rate)
