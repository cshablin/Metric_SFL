

class JavaCallGraphMetricExtractor(object):

    def __init__(self, java_call_graph_file, test_2_components):
        self._call_graph_file = java_call_graph_file
        self.test_2_interest_methods = test_2_components  # dict<test, dict<method_lowercase, parameters>>

    def get_connected_methods(self):
        """
        :return: dictionary <test_name, list<(f1, f2)>>
        """
        # initialize result
        result = {}
        for test in self.test_2_interest_methods.keys():
            result[test] = []

        with open(self._call_graph_file, 'r+') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                # M:class1:<method1>(arg_types) (typeofcall)class2:<method2>(arg_types)
                if line.startswith("M:"):
                    pair = line.split()
                    f1_struct = pair[0].split(":")
                    class1 = f1_struct[1]
                    method1_name = f1_struct[2].split("(")[0]
                    f1 = class1 + "." + method1_name

                    f2_struct = pair[1].split(":")
                    class2 = f2_struct[0].split(")")[1]
                    method2_name = f2_struct[1].split("(")[0]
                    f2 = class2 + "." + method2_name
                    for test, method_2_params in self.test_2_interest_methods.items():
                        f1_lower = f1.lower()
                        f2_lower = f2.lower()
                        if all(k in method_2_params for k in (f1_lower, f2_lower)):
                            result[test].append((f1_lower, f2_lower))

        return result



