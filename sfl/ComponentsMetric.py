
class ComponentsMetricType:
    def __init__(self):
        pass

    JavaCallGraphMetric = 1


class ComponentsMetricContext(object):
    def __init__(self, initial_tests, pool, bugs, errors, original_diagnosis):
        """

        :param initial_tests: list<'test'> defines test index order
        :param pool: dict<'test', [int]>
        :param bugs: list<int> components indexes
        :param errors: dict<'test', 0|1>
        :type original_diagnosis: list<'sfl.Diagnoser.Diagnosis.Diagnosis'>
        """
        self.initial_tests = initial_tests
        self.pool = pool
        self.bugs = bugs
        self.errors = errors
        self.original_diagnosis = original_diagnosis


class ComponentsMetric(object):

    def __init__(self, context, metric_descriptor):
        """

        :param context: ComponentsMetricContext
        :param metric_descriptor: <test_name, list<ExtractedComponents>>
        """
        self.context = context
        self.metric_descriptor = metric_descriptor
        self.original_matrix = None
        self.test_2_ordered_closest_comps = {}  # dict<test, list<int>>

    def change(self, matrix, tests_components):
        pass

    def factory(metric_type, regular_diagnose, metric_descriptor):

        if metric_type == ComponentsMetricType.JavaCallGraphMetric:
            return JavaCallGraphComponentsMetric(regular_diagnose, metric_descriptor)
        else:
            raise NotImplementedError("unsupported type {}".format(metric_type))
    factory = staticmethod(factory)


class JavaCallGraphComponentsMetric(ComponentsMetric):

    def __init__(self, regular_diagnose, metric_descriptor):
        ComponentsMetric.__init__(self, regular_diagnose, metric_descriptor)
        self.sorted_comps_by_order = {}
        self.combined_position = None

    def change(self, matrix, tests_components):
        self.original_matrix = [x[:] for x in matrix]
        for test, close_comps in self.metric_descriptor.items():
            close_comps_positions = self.calculate_closest_comps(close_comps)
            if close_comps_positions is not None:
                close_comps_positions = self.order(close_comps_positions, test)
            self.test_2_ordered_closest_comps[test] = close_comps_positions
            if close_comps_positions is not None:
                self.combine_columns(close_comps_positions, matrix, tests_components)

            # test_index = self.context.initial_tests.index(test)

    def calculate_closest_comps(self, close_comps):
        """

        :param close_comps: list<ExtractedComponents>
        :return: list<int>
        """
        connected_pairs_2_freq = {}
        max_freq = 0
        best_pair = None
        for close_comp in close_comps:
            # self.comps_names = comps_names
            # self.comps_positions = comps_positions
            key = tuple(close_comp.comps_positions)
            if key in connected_pairs_2_freq:
                connected_pairs_2_freq[key] += 1
            else:
                connected_pairs_2_freq[key] = 1
            if max_freq < connected_pairs_2_freq[key]:
                max_freq = connected_pairs_2_freq[key]
                best_pair = key
        if not best_pair:
            return None
        return list(best_pair)

    def combine_columns(self, close_comps_positions, matrix, tests_components):
        """

        :param tests_components: list<int>
        :param close_comps_positions: list<int>
        :param matrix: list< list<int> >
        :return:
        """
        # first column will include all others
        combined_position = close_comps_positions[0]
        for test_row in matrix:
            sum = 0
            for comp in close_comps_positions:
                sum += test_row[comp]
                test_row[comp] = 0
            if sum > 0:
                test_row[combined_position] = 1
        for test_components in tests_components:
            for to_omit in close_comps_positions[1:]:
                try:
                    test_components.remove(to_omit)
                except ValueError:
                    pass

    def order(self, close_comps_positions, test):
        """

        :param test: test name <unicode>
        :param close_comps_positions: list<int>
        :return: same list with high probable first order
        """
        from sfl.Diagnoser.Diagnosis import Diagnosis
        import operator

        result = []
        comp_2_order = {}
        original_diagnosis = self.context.original_diagnosis
        for comp in close_comps_positions:
            found_index = original_diagnosis.index(Diagnosis([comp]))
            comp_2_order[comp] = found_index

        self.sorted_comps_by_order[test] = sorted(comp_2_order.items(), key=operator.itemgetter(1))
        for t in self.sorted_comps_by_order[test]:
            if t[0] in self.context.bugs:
                result.insert(0, t[0])
            else:
                result.append(t[0])

        return result
