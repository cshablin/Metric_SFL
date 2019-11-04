__author__ = 'amir'

import csv
import math
import sys
from sfl_diagnoser.Diagnoser import Barinel

import Diagnosis
import Staccato
import TFOptimize


class BarinelOptimize(Barinel.Barinel):

    def __init__(self):
        super(BarinelOptimize, self).__init__()

    def tf_for_diag(self, diagnosis):
        return TFOptimize.TFOptimize(self.get_matrix(), self.get_error(), diagnosis).maximize()
