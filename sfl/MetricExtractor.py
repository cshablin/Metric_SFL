import json


class ExtractedComponents(object):
    def __init__(self, comps_names, comps_positions):
        """

        :param comps_names: list
        :param comps_positions: list
        """
        self.comps_names = comps_names
        self.comps_positions = comps_positions


class JavaCallGraphMetricExtractor(object):

    def __init__(self, java_call_graph_file, test_2_components, experiment_instance):
        """

        :param java_call_graph_file: generated file using the caller graph tool
        :param test_2_components: dictionary
        :param experiment_instance: ExperimentInstance
        """
        self._call_graph_file = java_call_graph_file
        self.test_2_interest_methods = test_2_components  # dict<test, dict<method_lowercase, parameters>>
        self.experiment_instance = experiment_instance

    def get_connected_methods(self):
        """
        :return: dictionary <test_name, list<ExtractedComponents>>
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
                                ec = self.get_extracted_components([f1_lower, f2_lower])
                                result[test].append(ec)

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

    def get_extracted_components(self, comps_list):
        resulting_positions = []
        for comp in comps_list:
            for position, comp_name in self.experiment_instance.components.items():
                if comp == str(comp_name):
                    resulting_positions.append(position)
        return ExtractedComponents(comps_list, resulting_positions)


class JpeekMetricExtractor(object):

    def __init__(self, jpeek_res_file, test_2_components, experiment_instance):
        """

        :param java_call_graph_file: generated file using the caller graph tool
        :param test_2_components: dictionary
        :param experiment_instance: ExperimentInstance
        :param jpeek_data: json dictionary where keys: class nams, value: dictionary of methods in class and LCOM distance
        """
        self._call_graph_file = jpeek_res_file
        self.test_2_interest_methods = test_2_components  # dict<test, dict<method_lowercase, parameters>>
        self.experiment_instance = experiment_instance
        with open(jpeek_res_file) as json_file:
            self.jpeek_data = json.load(json_file)
        print('jpeekMetricExtractor initilized')

    def get_connected_methods(self):
        """
        :return: dictionary <test_name, list<ExtractedComponents>>
        """
        # initialize result
        result = {}

        for test, method_2_params in self.test_2_interest_methods.items():
            result[test] = []
            for m in method_2_params:
                m = m.lower()
                C = self.get_class_of_method(m)
                class_methods = set(self.jpeek_data[C]["methods"])
                test_methods = set(method_2_params)
                mutual_methods = list(class_methods & test_methods - set(m))
                if self.jpeek_data[C]["distance"]>0.3:
                    for mutual_method in mutual_methods:
                        ec = self.get_extracted_components([m, mutual_method])
                        result[test].append((ec,self.jpeek_data[C]["distance"]))
                        # result[test].append(ec)
        return result


    def get_class_of_method(self, method_name):
        for class_name, class_data in self.jpeek_data.items():
            if method_name in class_data["methods"]:
                return class_name
        return ''

    def get_extracted_components(self, comps_list):
        resulting_positions = []
        for comp in comps_list:
            for position, comp_name in self.experiment_instance.components.items():
                if comp == str(comp_name):
                    resulting_positions.append(position)
        return ExtractedComponents(comps_list, resulting_positions)