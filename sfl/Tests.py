import unittest

from Diagnoser.diagnoserUtils import read_json_planning_file
from MetricExtractor import JavaCallGraphMetricExtractor


class MyTestCase(unittest.TestCase):

    def test_get_caller_graph_metric(self):
        ei = read_json_planning_file('..\\3131_56cd921f')
        raw_caller_graph = "..\\56cd921f.txt"

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
        ei.diagnose()


# if __name__ == '__main__':
#     unittest.main()
