# -*- coding: utf-8 -*-
"""
Created on Thu May 31 15:45:33 2018

@author: ai5982
"""

from genotype import Genotype
from world import World
import random
import copy

class Individual:
    
    def __init__(self, id, chromosome_size, trajectory):
        self.id = id
        self.fitness = 0.0
        self.genotype = Genotype()
        self.genotype.randomize(chromosome_size, trajectory)
        self.chromosome_size = chromosome_size
        
    def individualID(self):
        return self.id
    
    """
    TWO POINT CROSSOVER
    """
    def crossover(self, otherInd):
        #print("Individual " + str(self.id) + " is doing the crossover with Individual " + str(otherInd.id))
        #2-point-crossover
        
        lower_bound = random.randint(0, len(self.genotype.chromosomes) - 1)
        higher_bound = random.randint(lower_bound, len(self.genotype.chromosomes) - 1)        
        
        offsprings = []
        offsprings.append(copy.deepcopy(self))
        offsprings.append(copy.deepcopy(otherInd))
        
        for i in range(lower_bound, higher_bound + 1):
            offsprings[0].getGenotype().chromosomes[i] = otherInd.getGenotype().chromosomes[i]
            offsprings[1].getGenotype().chromosomes[i] = self.getGenotype().chromosomes[i]
        
        
        #Check for validity of the world
        world_validity = World(offsprings[0].getPhenotype().level)
        if world_validity.validate_trajectory(offsprings[0].getGenotype().trajectory) == False:
            offsprings[0] = copy.deepcopy(self)
        if world_validity.validate_trajectory(offsprings[1].getGenotype().trajectory) == False:
            offsprings[1] = copy.deepcopy(otherInd)
        
        return offsprings 
    
    """
    Mutate an individual chromosome! (called from the algorithm!)
    """
    def mutate(self, mutation_probability):
        possible_tiles = [0,1,5,6,7,8]
        #print("Individual " + str(self.id) + " is MUTATING")
        if random.uniform(0,1) < mutation_probability:
            self.genotype.chromosomes[random.randint(0, len(self.genotype.chromosomes) - 1)] = possible_tiles[random.randint(0, len(possible_tiles) - 1)]
        return
    
    """
    Test each chromosome for mutation
    """
    def mutateAll(self, mutation_probability):
        possible_tiles = [0,1,5,6,7,8]
        chromosome_size = len(self.genotype.chromosomes)
        for i in range(chromosome_size):
            if random.uniform(0, 1) < mutation_probability:
                self.genotype[i] = possible_tiles[random.randint(0, len(possible_tiles) - 1)]
    
    def setFitness(self, fitness):
        self.fitness = fitness
        
    def getFitness(self):
        return self.fitness
    
    def getGenotype(self):
        return self.genotype
    
    def getPhenotype(self):
        return self.genotype.getPhenotype()