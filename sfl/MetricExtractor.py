

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
                    func1 = self.shorten_parameters(f1_struct[2])
                    f1 = f1_struct[1] + "." + func1

                    f2_struct = pair[1].split(":")
                    class2 = f2_struct[0].split(")")[1]
                    func2 = self.shorten_parameters(f2_struct[1])
                    f2 = class2 + "." + func2

                    for test, method_2_params in self.test_2_interest_methods.items():
                        f1_lower = f1.lower()
                        f2_lower = f2.lower()
                        if f1_lower in method_2_params:
                            if f2_lower in method_2_params:
                                result[test].append((f1_lower, f2_lower))

        return result

    def shorten_parameters(self, func):
        import re
        split1 = re.split('\(|\)', func)
        method_name = split1[0]
        method_params = split1[1]
        if not method_params:
            return method_name + '()'
        result = method_name + '('
        full_named_parameters = method_params.split(',')
        counter = 1
        total_params = len(full_named_parameters)
        for full_param in full_named_parameters:
            all_param_names = full_param.split('.')
            param_name = all_param_names[len(all_param_names) - 1].lower()
            result += param_name
            if counter < total_params:
                result += ';'
            counter += 1

        return result + ')'
