# -*- coding: utf-8 -*-
"""
Created on Thu May 31 15:46:17 2018

@author: ai5982
"""
import numpy as np

class Phenotype:
    
    #Add the map as a genotype and phenotype
    
    def __init__(self, level):
        self.a = 0
        self.level = level
        
    def levelFromChromosomes(self, chromosomes, trajectory, width, height):
        matrix = chromosomes.reshape(height, width)
        self.level.generate_from_matrix(matrix, trajectory)
        
    