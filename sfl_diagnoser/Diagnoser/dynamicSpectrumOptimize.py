import sfl_diagnoser.Diagnoser
from sfl_diagnoser.Diagnoser.FullMatrixOptimize import FullMatrixOptimize
import sfl_diagnoser.Diagnoser.dynamicSpectrum
from functools import partial


class dynamicSpectrumOptimize(sfl_diagnoser.Diagnoser.dynamicSpectrum.dynamicSpectrum):
    def __init__(self):
        super(dynamicSpectrumOptimize, self).__init__()

    def _create_full_matrix(self):
        return FullMatrixOptimize()
