import unittest
from os import listdir, path

from sfl.ComponentsMetric import ComponentsMetric, ComponentsMetricType, ComponentsMetricContext
from sfl.Diagnoser.Diagnosis_Results import Diagnosis_Results
from sfl.Diagnoser.diagnoserUtils import read_json_planning_file
from sfl.MetricExtractor import JpeekMetricExtractor


class MyTestCase(unittest.TestCase):

    maven_matrices_folder = 'Data\\maven\\matrices'
    maven_caller_graph_folder = 'Data\\maven\\jpeek_LCOM_extracted_weighted_results'
    wicket_matrices_folder = 'Data\\wicket\\matrices'
    wicket_caller_graph_folder = 'Data\\wicket\\jpeek_LCOM_extracted_weighted_results'

    def test_get_caller_graph_metric(self):
        ei = read_json_planning_file('Data\\maven\\matrices\\3131_56cd921f')
        raw_caller_graph = 'Data\\maven\\\jpeek_LCOM_extracted_weighted_results\\56cd921f.json'
        print('ok')
        test_2_components = self.get_inspection_2_comps(ei)

        metric_extractor = JpeekMetricExtractor(raw_caller_graph, test_2_components, ei)
        test_2_connected_components = metric_extractor.get_connected_methods() # get connected methods need to return conneceted methods in each tets which are relevant to that test  -the majority of the work!
        1
    def get_inspection_2_comps(self, ei):  # return failed test with thier components
        test_2_components = {}  # dict<test, dict<method_lowercase, parameters>>
        for test, is_failed in ei.error.items():
            if is_failed:
                comps_ints = ei.pool[test]
                methods = {}
                for i in comps_ints:
                    comp_name = str(ei.components[i])
                    method_split = comp_name.split('(')
                    # methods[method_split[0]] = method_split[1].strip(')')
                    methods[comp_name] = method_split[1].strip(')')
                test_2_components[test] = methods
        return test_2_components

    def test_get_caller_graph_metric_all_commits(self):
        result = self.get_commits_2_metrics(self.maven_matrices_folder, self.maven_caller_graph_folder)

        self.assertEqual(len(result['3616_912a565f'][unicode(u'org.apache.maven.settings.validation.defaultsettingsvalidatortest.testvalidatemirror')]), 1)

    @unittest.skip("testing skipping")
    def test_maven_diagnosis_using_caller_graph_metrics(self):
        print('    def test_maven_diagnosis_using_caller_graph')
        commits_2_tests_metrics = self.get_commits_2_metrics(self.maven_matrices_folder, self.maven_caller_graph_folder)
        waisted_regular = []
        waisted_metric = []
        for commit_matrix, test_2_connected_components in commits_2_tests_metrics.items():

            experiment_instance = read_json_planning_file(path.join(self.maven_matrices_folder, commit_matrix))
            print("without metric {}:".format(commit_matrix))
            result = self.diagnose(experiment_instance, None)
            waisted_regular.append(result.metrics['wasted'])
            original_diagnoses = experiment_instance.diagnoses

            experiment_instance = read_json_planning_file(path.join(self.maven_matrices_folder, commit_matrix))
            context = ComponentsMetricContext(experiment_instance.initial_tests, experiment_instance.pool,
                                              experiment_instance.get_id_bugs(), experiment_instance.error,
                                              original_diagnoses)
            call_graph_components_metric = ComponentsMetric.factory(ComponentsMetricType.JpeekMetric,
                                                                    context, test_2_connected_components)
            print("with metric {}:".format(commit_matrix))
            result = self.diagnose(experiment_instance, call_graph_components_metric)
            waisted_metric.append(result.metrics['wasted'])
        print ("waisted regular: ", waisted_regular)
        print ("waisted metric : ", waisted_metric)

    def test_wicket_diagnosis_using_caller_graph_metrics(self):
        commits_2_tests_metrics = self.get_commits_2_metrics(self.wicket_matrices_folder, self.wicket_caller_graph_folder)
        # commits_2_tests_metrics = self.get_commits_2_metrics(self.wicket_matrices_folder, self.wicket_caller_graph_folder, '5426_fb45a781')
        # temp = {}
        # temp['5486_a79ed51e'] = commits_2_tests_metrics['5486_a79ed51e']
        # temp['5582_1fb66533'] = commits_2_tests_metrics['5582_1fb66533']
        # temp['5426_fb45a781'] = commits_2_tests_metrics['5426_fb45a781']
        waisted_regular = []
        waisted_metric = []
        for commit_matrix, test_2_connected_components in commits_2_tests_metrics.items():
            try:
                experiment_instance = read_json_planning_file(path.join(self.wicket_matrices_folder, commit_matrix))
                result = self.diagnose(experiment_instance, None)
                waisted_regular.append(result.metrics['wasted'])
                print("without metric {} cost {}".format(commit_matrix, result.metrics['wasted']))
                original_diagnoses = experiment_instance.diagnoses

                experiment_instance = read_json_planning_file(path.join(self.wicket_matrices_folder, commit_matrix))
                context = ComponentsMetricContext(experiment_instance.initial_tests, experiment_instance.pool,
                                                  experiment_instance.get_id_bugs(), experiment_instance.error,
                                                  original_diagnoses)
                call_graph_components_metric = ComponentsMetric.factory(ComponentsMetricType.JpeekMetric,
                                                              v             context, test_2_connected_components)
                result1 = self.diagnose(experiment_instance, call_graph_components_metric)
                waisted_metric.append(result1.metrics['wasted'])
                print("with metric {} cost {}".format(commit_matrix, result1.metrics['wasted']))
            except:
                print('metric {} crashed'.format(commit_matrix))
        print ("waisted regular: ", waisted_regular)
        print ("waisted metric : ", waisted_metric)

    def diagnose(self, experiment_instance, call_graph_components_metric):
        experiment_instance.set_comps_metric(call_graph_components_metric)
        experiment_instance.diagnose()
        return Diagnosis_Results(experiment_instance.diagnoses, experiment_instance.initial_tests, experiment_instance.error,
                                 experiment_instance.pool, experiment_instance.get_id_bugs(), call_graph_components_metric)
        # print(Diagnosis_Results(experiment_instance.diagnoses, experiment_instance.initial_tests, experiment_instance.error,
        #                         experiment_instance.pool, experiment_instance.get_id_bugs(), call_graph_components_metric).metrics)

    def get_commits_2_metrics(self, matrices_folder, caller_graph_folder, commit_id = None):
        result = {}
        for matrix in listdir(matrices_folder):
            try:
                print('extracted commit: {} '.format(matrix))
                raw_caller_graph = path.join(caller_graph_folder, matrix.split('_')[1] + '.json')
                if not path.exists(raw_caller_graph):  # for wicket we didn't generate all commits graphs
                    continue
                if commit_id is not None:
                    if matrix != commit_id:
                        continue
                ei = read_json_planning_file(path.join(matrices_folder, matrix))

                test_2_components = self.get_inspection_2_comps(ei)
                metric_extractor = JpeekMetricExtractor(raw_caller_graph, test_2_components, ei)
                # dictionary <test_name, list<(f1, f2)>>
                test_2_connected_components = metric_extractor.get_connected_methods()
                result[matrix] = test_2_connected_components
                print ("json {} succesed loaded, error".format(matrix))
            except Exception as e:
                print ("json {} could not be loaded, error {}".format(matrix, type(e).__name__))
        return result

# if __name__ == '__main__':
#     unittest.main()
