# -*- coding: utf-8 -*-
"""
Created on Thu May 31 15:44:57 2018

@author: ai5982
"""

from individual import Individual
from level import Level
from trajectory import Trajectory, RandomWalkTrajectory
from search import WorldGraph, a_star_search
from world import World
import operator
import random

class Algorithm:
      
    def __init__(self, trajectory, width, height, population_size, generations, chromosome_size, mutation_probability=0.5, tournament_size = 5):
        self.population = []
        self.population_size = population_size
        self.generations = generations
        self.chromosome_size = chromosome_size
        self.offspring_size = population_size//2
        self.tournament_size = tournament_size
        self.mutation_probability = mutation_probability
        self.trajectory = trajectory
        self.level_width = width
        self.level_height = height
        self.best = None
        self.best_generations = []
          
    """
    Test get population
    """
    def getPopulationSize(self):
        return len(self.population)
    
    """
    Initialize the population depending on the size
    The "randomizer" is in the genotype which is called by the individual when created
    """
    def initializePopulation(self):
        for i in range(self.population_size):
            self.population.append(Individual(i, self.chromosome_size, self.trajectory))
        return
    
    
    """
    Evaluate the whole population by the fitness function
    """
    def evaluatePopulation(self):
        for individual in self.population:
            individual.setFitness(self.calculateFitness(individual))
#            print("fitness is = " + str(individual.getFitness()))
#            individual.getPhenotype().level.print()
        self.population.sort(key=operator.attrgetter('fitness'), reverse=True)
    
    """
    Fitness FUNCTION!
    """
    def calculateFitness(self, individual):
        #print("calculating...")
        phen = individual.getPhenotype()
        world = World(phen.level)
        state = world.init_state
        exit_position, exit_cell = phen.level.get_exit()
        
        #Calculate the cost of traversing the level
        came_from, cost_so_far, current, n_steps = a_star_search(
        graph=WorldGraph(world), start=state,
            exit_definition=exit_position,
            extract_definition=world.get_player_position)
        
        return n_steps
        
    """
    Select individuals doing tournament selection and reproduce the parents
    """    
    def selectIndividuals(self):
        offsprings = []
        #print("Select from the whole population and create offsprings half the size... Tournament selection")
        
        while(len(offsprings) < self.offspring_size):
            parents = random.sample(self.population, self.tournament_size)
            parents.sort(key=operator.attrgetter('fitness'), reverse=True)
            offsprings.extend(parents[0].crossover(parents[1]))
            
        return offsprings
    
    """
    Mutate all population by mutation probability
    """
    def mutatePopulation(self):
        for individual in self.population:
            individual.mutate(self.mutation_probability)
    
    def replaceIndividuals(self, new_individuals):
        #print("Replace the half of the individuals? ... 50% elitism")
        #print(len(new_individuals))
        while(len(new_individuals) > self.offspring_size):
             del new_individuals[len(new_individuals) - 1]

        #print(len(new_individuals))
        self.population[self.offspring_size : len(self.population)] = new_individuals
        
    """
    Print the current best individual
    """
    def printBestIndividual(self):
        print("BEST INDIVIDUAL IS: " + 
              str(self.population[0].individualID()) + 
              " with a fitness of: " + 
              str(self.population[0].getFitness()))
        
        self.best = self.population[0]
        self.best_generations.append(str("BEST INDIVIDUAL IS: " + 
              str(self.population[0].individualID()) + 
              " with a fitness of: " + 
              str(self.population[0].getFitness())))
#        print(self.population[0].getGenotype().chromosomes)
        #self.population[0].getPhenotype().level.print()
        
    def printBestGenerations(self):
        print(self.best_generations)

    """
    Runs the algorithm one generation at a time.
    """
    def run(self):
        self.initializePopulation()
        print("dsdsds")
        for i in range(self.generations):
            self.evaluatePopulation()
            yield self.population[0].getPhenotype().level  # TODO FIX COPY
            self.printBestIndividual()
            offsprings = self.selectIndividuals()
            self.replaceIndividuals(offsprings)
            self.mutatePopulation()

        self.evaluatePopulation()
        yield self.population[0].getPhenotype().level

#trajectory = RandomWalkTrajectory(40, 30)
#evolutionaryAlgorithm = Algorithm(trajectory, width=40, height=30, population_size=10, generations=10, chromosome_size=100)
#evolutionaryAlgorithm.run()
#evolutionaryAlgorithm.printBestIndividual()

