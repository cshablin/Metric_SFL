from sfl_diagnoser.Diagnoser.diagnoserUtils import readPlanningFile
from sfl_diagnoser.Diagnoser.Diagnosis_Results import Diagnosis_Results
from operator import itemgetter
import sfl_diagnoser.Diagnoser.Experiment_Data
import sfl_diagnoser.Diagnoser.ExperimentInstance
import sfl_diagnoser.Planner.HP_Random
import timeit
import time
import os

def run_dignose_eyal(bug_id, RESULTS_FILE, ADDITIONAL_FILES_PATH):
    print("Start diagnose")
    start = time.time()
    #amir results
    list_pre_amir, list_recall_amir = get_diagnose_results(ADDITIONAL_FILES_PATH,1,os.path.join(ADDITIONAL_FILES_PATH , r'inputMatrix_amir.txt'))
    print("Actual")
    #eyal results
    list_pre_eyal_1, list_recall_eyal_1 = get_diagnose_results(ADDITIONAL_FILES_PATH,2,os.path.join(ADDITIONAL_FILES_PATH , r'inputMatrix_eyal_1.txt'))
    print("Predicted")
    # list_pre_eyal_2, list_recall_eyal_2 = get_diagnose_results(ADDITIONAL_FILES_PATH,2,os.path.join(ADDITIONAL_FILES_PATH , r'inputMatrix_eyal_2.txt'))
    # print("Eyal_2")
    # list_pre_eyal_3, list_recall_eyal_3 = get_diagnose_results(ADDITIONAL_FILES_PATH,2,os.path.join(ADDITIONAL_FILES_PATH , r'inputMatrix_eyal_3.txt'))
    # print("Eyal_3")
    # random results
    list_pre_random, list_recall_random = get_diagnose_results(ADDITIONAL_FILES_PATH, 3, os.path.join(ADDITIONAL_FILES_PATH , r'inputMatrix_amir.txt'))
    print("Th")

    # list_pre_amir = [2]
    if len(list_pre_amir)>0:
        write_result_to_file(RESULTS_FILE, bug_id, "Oracle", list_pre_amir, list_recall_amir, 1)
        write_result_to_file(RESULTS_FILE, bug_id, "Prob", list_pre_eyal_1, list_recall_eyal_1, 2)
        # write_result_to_file(RESULTS_FILE, bug_id, "Eyal_2", list_pre_eyal_2, list_recall_eyal_2, 2)
        # write_result_to_file(RESULTS_FILE, bug_id, "Eyal_3", list_pre_eyal_3, list_recall_eyal_3, 2)
        write_result_to_file(RESULTS_FILE, bug_id, "Random", list_pre_random, list_recall_random, 3)
    total_diagnose_time = time.time() - start
    print("Total diagnose time: " + str(total_diagnose_time))
    i=5


def write_result_to_file(RESULTS_FILE, bug_id, name, list_pre, list_recall,param):
    with open(RESULTS_FILE, 'a') as fd:
        if param == 1:
            fd.write("Bug num " + str(bug_id) + "\n")
        fd.write(str(name) + "\n")
        fd.write("Precision" + "\n")
        str_pre = ','.join([str(x) for x in list_pre])
        fd.write(str_pre + "\n")
        fd.write("Recall" + "\n")
        str_recall = ','.join([str(x) for x in
                               list_recall])
        fd.write(str_recall + "\n")


def get_diagnose_results(ADDITIONAL_FILES_PATH,param,file_path):
    instAmir = readPlanningFile(file_path)
    instAmir.diagnose()
    list_pre, list_recall = sfl_diagnoser.Planner.HP_Random.main_HP(instAmir,param)
    return list_pre, list_recall


if __name__ == '__main__':
    print("start init diagnoser")
    start_t = timeit.default_timer()
    run_dignose_eyal("2",r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\results3.csv', r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_2_fix\additionalFiles')
    total_t = timeit.default_timer() - start_t
    print("get_diagnose_results: " + str(total_t / 60) + "\r\n")
