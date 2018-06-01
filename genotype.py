# -*- coding: utf-8 -*-
"""
Created on Thu May 31 15:46:00 2018

@author: ai5982
"""

from phenotype import Phenotype
from level import Level
import numpy as np
import random

class Genotype:
    
    #Add the map as a genotype and phenotype
    def __init__(self):
        self.chromosomes = np.zeros(0, dtype=int)

    def randomize(self, chromosomeSize, trajectory):
        self.level = Level(40,30)
        self.level.generate_from_trajectory(trajectory, random.uniform(0,1))
        self.phenotype = Phenotype(self.level)
        self.chromosomes = self.level.cells
        self.chromosomes = self.chromosomes.flatten()
#        np.set_printoptions(threshold=np.nan)
#        print(self.chromosomes)
#        print("another genotype")
        
        """
        for i in range(chromosomeSize):
            self.chromosomes.append(random.randint(0,1))
        """
            
    def getPhenotype(self):
        self.phenotype.levelFromChromosomes(self.chromosomes)
        return self.phenotype