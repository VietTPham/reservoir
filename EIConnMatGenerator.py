# version: Python 3.7
__author__ = 'Tarek, Isabel'

import csv
import numpy
from os import path, makedirs


class ConnectivityMatrixGenerator(object):

    def __init__(self, n_excite, n_inhib, p_ee, p_ei, p_ie, p_ii):

        # Determine numbers of neurons
        self.n_excite = n_excite
        self.n_inhib = n_inhib
        self.n_neurons = n_excite + n_inhib

        # Initialize connectivity matrix
        self.conn_mat = numpy.zeros((self.n_neurons, self.n_neurons))

        # Initialize weight matrix
        self.weight_mat = numpy.zeros((self.n_neurons, self.n_neurons))

        # Calculate total number of connections per neuron (remove neuron from target if included (ee and ii))
        self.k_ii = int(round(p_ii * (self.n_inhib - 1)))
        self.k_ei = int(round(p_ei * self.n_inhib))
        self.k_ie = int(round(p_ie * self.n_excite))
        self.k_ee = int(round(p_ee * (self.n_excite - 1)))

    def run_generator(self):

        try:

            # Generate connectivity matrix and check that it's successful
            if not self.generate_conn_mat():
                raise Exception('Failed to generate connectivity matrix.')
            print("Connectivity Matrix Generated")

            # Generate weight matrix and check that it's successful
            if not self.make_weighted():
                raise Exception('Failed to weight connectivity matrix.')
            print("Weighted")

            return self.weight_mat

        except Exception as e:
            print(e)
            return False

    def generate_conn_mat(self):

        try:

            # E to E connections
            for n in range(0, self.n_excite):
                for a in range(0, self.k_ee):
                    rand = numpy.random.randint(0, self.n_excite)
                    while rand == n or self.conn_mat[n][rand] == 1:
                        rand = numpy.random.randint(0, self.n_excite)
                    self.conn_mat[n][rand] = 1
            
            # E to I connections
            for n in range(0, self.n_excite):
                for a in range(0, self.k_ei):
                    rand = numpy.random.randint(self.n_excite, self.n_excite + self.n_inhib)
                    while self.conn_mat[n][rand] == 1:
                        rand = numpy.random.randint(self.n_excite, self.n_excite + self.n_inhib)
                    self.conn_mat[n][rand] = 1
            
            # I to E connections
            for n in range(0, self.n_inhib):
                for a in range(0, self.k_ie):
                    rand = numpy.random.randint(0, self.n_excite)
                    while self.conn_mat[n + self.n_excite][rand] == 1:
                        rand = numpy.random.randint(0, self.n_excite)
                    self.conn_mat[n + self.n_excite][rand] = 1
            
            # I to I connections
            for n in range(0, self.n_inhib):
                for a in range(0, self.k_ii):
                    rand = numpy.random.randint(self.n_excite, self.n_excite + self.n_inhib)
                    while rand == (n + self.n_excite) or self.conn_mat[n + self.n_excite][rand] == 1:
                        rand = numpy.random.randint(self.n_excite, self.n_excite + self.n_inhib)
                    self.conn_mat[n + self.n_excite][rand] = 1
            
            return True

        except Exception as e:
            print(e)
            return False

    def make_weighted(self):

        try:

            # Generate random weights and fill matrix
            for i in range(0, self.n_neurons):
                for j in range(0, self.n_neurons):
                    if self.conn_mat[i][j] == 1:
                        self.weight_mat[i][j] = (numpy.random.lognormal(-0.64, 0.51))
                        # Make all I 10 times stronger AND NEGATIVE
                        if self.n_neurons > i > (self.n_neurons - self.n_inhib):
                            self.weight_mat[i][j] = - self.weight_mat[i][j] * 10

            return True

        except Exception as e:
            print(e)
            return False
