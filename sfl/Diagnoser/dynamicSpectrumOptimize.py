import sfl.Diagnoser
from sfl.Diagnoser.FullMatrixOptimize import FullMatrixOptimize
import sfl.Diagnoser.dynamicSpectrum
from functools import partial


class dynamicSpectrumOptimize(sfl.Diagnoser.dynamicSpectrum.dynamicSpectrum):
    def __init__(self):
        super(dynamicSpectrumOptimize, self).__init__()

    def _create_full_matrix(self):
        return FullMatrixOptimize()
