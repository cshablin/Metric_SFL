from sfl.Diagnoser.diagnoserUtils import write_json_planning_file, read_json_planning_instance, read_json_planning_file
from sfl.Diagnoser.Experiment_Data import Experiment_Data
from sfl.Diagnoser.Diagnosis_Results import Diagnosis_Results

ei = read_json_planning_file(r'5a509030a946646780e963b9f492a4eaff734116')
ei.diagnose()
print(Diagnosis_Results(ei.diagnoses, ei.initial_tests, ei.error, ei.pool, ei.get_id_bugs()).metrics)