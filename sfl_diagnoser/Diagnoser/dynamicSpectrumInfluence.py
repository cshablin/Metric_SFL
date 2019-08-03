import sfl_diagnoser.Diagnoser
from sfl_diagnoser.Diagnoser.FullMatrixInfluence import FullMatrixInfluence
import sfl_diagnoser.Diagnoser.dynamicSpectrum


class DynamicSpectrumInfluence(sfl_diagnoser.Diagnoser.dynamicSpectrum.dynamicSpectrum):
    def __init__(self):
        super(DynamicSpectrumInfluence, self).__init__()
        self.influence_matrix = dict()
        self.influence_alpha = 0

    def set_influence_matrix(self, matrix):
        self.influence_matrix = matrix

    def set_influence_alpha(self, alpha):
        self.influence_alpha = alpha

    def convertToFullMatrix(self):
        ans=FullMatrixInfluence()
        ans.probabilities=list(self.getprobabilities())
        ans.error=list(self.geterror())
        ans.matrix = map(lambda test: map(lambda comp: 1 if comp in test else 0, range(len(self.getprobabilities()))), self.getTestsComponents())
        influence_matrix = []
        for test_id, test in enumerate(self.getTestsComponents()):
            test_data = []
            for comp in range(len(self.getprobabilities())):
                test_data.append(self.influence_matrix[test_id][comp] if comp in test else 0)
            influence_matrix.append(test_data)
        ans.influence_matrix = influence_matrix
        ans.influence_alpha = self.influence_alpha
        return ans

