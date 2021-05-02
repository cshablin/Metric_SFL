from sfl.Diagnoser.diagnoserUtils import write_json_planning_file, read_json_planning_instance, read_json_planning_file
from sfl.Diagnoser.Experiment_Data import Experiment_Data
from sfl.Diagnoser.Diagnosis_Results import Diagnosis_Results

ei = read_json_planning_file(r'506bd018b3ca638cd0c9d1bdad627f6468a05bee')
ei.diagnose()
print(Diagnosis_Results(ei.diagnoses, ei.initial_tests, ei.error, ei.pool, ei.get_id_bugs()).metrics)