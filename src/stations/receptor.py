import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import rebroadcast.messages as m
import middleware.constants as cons
from middleware.channels import InterNode, InterProcess

from multiprocessing import Process

class Receptor(Process):

    def __init__(self, country, frequency, config):

        self.country = country
        self.frequency = frequency
        self.config = config

        super(Receptor, self).__init__()

    def run(self):
        pass

