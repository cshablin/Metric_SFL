import unittest
from os import listdir, path

from sfl.Diagnoser.diagnoserUtils import read_json_planning_file
from sfl.MetricExtractor import JavaCallGraphMetricExtractor


class MyTestCase(unittest.TestCase):

    maven_matrices_folder = 'Data\\maven\\matrices'
    maven_caller_graph_folder = 'Data\\maven\\raw_caller_graphs'

    def test_get_caller_graph_metric(self):
        ei = read_json_planning_file('Data\\maven\\matrices\\3131_56cd921f')
        raw_caller_graph = 'Data\\maven\\raw_caller_graphs\\56cd921f.txt'

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


        metric_extractor = JavaCallGraphMetricExtractor(raw_caller_graph, test_2_components)
        test_2_connected_components = metric_extractor.get_connected_methods()

    def test_get_caller_graph_metric_all_commits(self):
        for matrix in listdir(self.maven_matrices_folder):
            try:
                ei = read_json_planning_file(path.join(self.maven_matrices_folder, matrix))
            except Exception as e:
                print ("json {} could not be loaded, error {}".format(matrix, type(e).__name__))


# if __name__ == '__main__':
#     unittest.main()
