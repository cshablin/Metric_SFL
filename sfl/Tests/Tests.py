import unittest
from os import listdir, path

from sfl.ComponentsMetric import ComponentsMetric, ComponentsMetricType
from sfl.Diagnoser.Diagnosis_Results import Diagnosis_Results
from sfl.Diagnoser.diagnoserUtils import read_json_planning_file
from sfl.MetricExtractor import JavaCallGraphMetricExtractor


class MyTestCase(unittest.TestCase):

    maven_matrices_folder = 'Data\\maven\\matrices'
    maven_caller_graph_folder = 'Data\\maven\\raw_caller_graphs'

    def test_get_caller_graph_metric(self):
        ei = read_json_planning_file('Data\\maven\\matrices\\3131_56cd921f')
        raw_caller_graph = 'Data\\maven\\raw_caller_graphs\\56cd921f.txt'

        test_2_components = self.get_inspection_2_comps(ei)

        metric_extractor = JavaCallGraphMetricExtractor(raw_caller_graph, test_2_components)
        test_2_connected_components = metric_extractor.get_connected_methods()

    def get_inspection_2_comps(self, ei):
        test_2_components = {}  # dict<test, dict<method_lowercase, parameters>>
        for test, is_failed in ei.error.items():
            if is_failed:
                comps_ints = ei.pool[test]
                methods = {}
                for i in comps_ints:
                    comp_name = str(ei.components[i])
                    method_split = comp_name.split('(')
                    methods[method_split[0]] = method_split[1].strip(')')
                test_2_components[test] = methods
        return test_2_components

    def test_get_caller_graph_metric_all_commits(self):
        result = self.get_maven_commits_2_metrics()

        self.assertEqual(len(result['3616_912a565f'][unicode(u'org.apache.maven.settings.validation.defaultsettingsvalidatortest.testvalidatemirror')]), 1)

    # @unittest.skip("testing skipping")
    def test_diagnosis_using_caller_graph_metrics(self):
        commits_2_tests_metrics = self.get_maven_commits_2_metrics()
        for commit_matrix, test_2_connected_components in commits_2_tests_metrics.items():
            experiment_instance = read_json_planning_file(path.join(self.maven_matrices_folder, commit_matrix))
            call_graph_components_metric = ComponentsMetric.factory(ComponentsMetricType.JavaCallGraphMetric, None, test_2_connected_components)
            experiment_instance.set_comps_metric(call_graph_components_metric)
            experiment_instance.diagnose()
            print(Diagnosis_Results(experiment_instance.diagnoses, experiment_instance.initial_tests, experiment_instance.error,
                                    experiment_instance.pool, experiment_instance.get_id_bugs()).metrics)

    def get_maven_commits_2_metrics(self):
        result = {}
        for matrix in listdir(self.maven_matrices_folder):
            try:
                ei = read_json_planning_file(path.join(self.maven_matrices_folder, matrix))

                test_2_components = self.get_inspection_2_comps(ei)
                raw_caller_graph = path.join(self.maven_caller_graph_folder, matrix.split('_')[1] + '.txt')
                metric_extractor = JavaCallGraphMetricExtractor(raw_caller_graph, test_2_components)
                # dictionary <test_name, list<(f1, f2)>>
                test_2_connected_components = metric_extractor.get_connected_methods()
                result[matrix] = test_2_connected_components
            except Exception as e:
                print ("json {} could not be loaded, error {}".format(matrix, type(e).__name__))
        return result

# if __name__ == '__main__':
#     unittest.main()
