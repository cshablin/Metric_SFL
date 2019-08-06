from sfl_diagnoser.Diagnoser.diagnoserUtils import readPlanningFile
from sfl_diagnoser.Diagnoser.Diagnosis_Results import Diagnosis_Results
import sfl_diagnoser.Diagnoser.ExperimentInstance


inst = readPlanningFile("C:\\Users\\eyalhad\\Desktop\\SFL-diagnoser\\MatrixFile2.txt")
inst.diagnose()
results = Diagnosis_Results(inst.diagnoses, inst.initial_tests, inst.error)
results.get_metrics_names()
results.get_metrics_values()
ei = sfl_diagnoser.Diagnoser.ExperimentInstance.addTests(inst, inst.hp_next_by_prob())
i=5