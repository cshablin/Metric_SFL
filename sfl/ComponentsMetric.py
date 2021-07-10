
class ComponentsMetricType:
    def __init__(self):
        pass

    JavaCallGraphMetric = 0
    JpeekMetric = 1


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
        self.test_2_ordered_closest_comps = {}  # dict<test, (list<int>, score)>

    def change(self, matrix, tests_components):
        pass

    def factory(metric_type, regular_diagnose, metric_descriptor):

        if metric_type == ComponentsMetricType.JavaCallGraphMetric:
            return JavaCallGraphComponentsMetric(regular_diagnose, metric_descriptor)
        elif metric_type == ComponentsMetricType.JpeekMetric:
            return JpeekDistanceComponentsMetric(regular_diagnose, metric_descriptor)
        else:
            raise NotImplementedError("unsupported type {}".format(metric_type))
    factory = staticmethod(factory)


class JavaCallGraphComponentsMetric(ComponentsMetric):

    def __init__(self, regular_diagnose, metric_descriptor):
        ComponentsMetric.__init__(self, regular_diagnose, metric_descriptor)
        self.sorted_comps_by_order = {}
        self.combined_position = None
        self.actual_coned_positions = []  # list<list<position>>
        print('init JavaCallGraphComponentsMetric')

    def change(self, matrix, tests_components):
        self.original_matrix = [x[:] for x in matrix]
        for test, close_comps in self.metric_descriptor.items():
            close_comps_positions, close_comps_score = self.calculate_closest_comps(close_comps)
            if close_comps_positions is not None:
                close_comps_positions = self.order(close_comps_positions, test)
            self.test_2_ordered_closest_comps[test] = close_comps_positions, close_comps_score
        if len(self.test_2_ordered_closest_comps) > 0:
            self.combine_columns(self.test_2_ordered_closest_comps, matrix, tests_components)

            # test_index = self.context.initial_tests.index(test)

    def calculate_closest_comps(self, close_comps):
        """

        :param close_comps: list<ExtractedComponents>
        :return: list<int> , frequency score (for using in column combining)
        """
        connected_pairs_2_freq = {}
        comp_position_2_freq = {}
        max_pair_freq = 0
        best_pair = None

        for close_comp in close_comps:

            for pos in close_comp.comps_positions:
                if pos in comp_position_2_freq:
                    comp_position_2_freq[pos] += 1
                else:
                    comp_position_2_freq[pos] = 1

            # self.comps_names = comps_names
            # self.comps_positions = comps_positions
            key = tuple(close_comp.comps_positions)
            if key in connected_pairs_2_freq:
                connected_pairs_2_freq[key] += 1
            else:
                connected_pairs_2_freq[key] = 1
            if max_pair_freq < connected_pairs_2_freq[key]:
                max_pair_freq = connected_pairs_2_freq[key]
                best_pair = key
        if not best_pair:
            return None, None
        best_pair_list = list(best_pair)
        individual_max_freq = 0
        for pos in best_pair_list:
            if comp_position_2_freq[pos] > individual_max_freq:
                individual_max_freq = comp_position_2_freq[pos]

        # print ("best pair {} score {}".format(best_pair_list, float(max_pair_freq + individual_max_freq) / len(close_comps)))
        return best_pair_list, max_pair_freq + individual_max_freq

    def combine_columns(self, test_2_ordered_closest_comps, matrix, tests_components):
        """

        :param tests_components: list<int>
        :param test_2_ordered_closest_comps: dict< test, (list<int>, score)>
        :param matrix: list< list<int> >
        :return:
        """
        allready_omitted = []
        common_comp_2_tests = self.calculate_common_close_comps_between_tests(test_2_ordered_closest_comps)

        #  This code choose to cone more than 2 comps
        # if len(common_comp_2_tests) > 0:
        #     resulting_cone = []
        #     for common_comp, tests in common_comp_2_tests.items():
        #         for test in tests:
        #             for comp in test_2_ordered_closest_comps[test][0]:
        #                 if comp not in resulting_cone:
        #                     resulting_cone.append(comp)
        #
        #     self.actual_coned_positions.append(resulting_cone)
        #     # first column will include all others
        #     combined_position = resulting_cone[0]
        #     for test_row in matrix:
        #         summation = 0
        #         for comp in resulting_cone:
        #             summation += test_row[comp]
        #             test_row[comp] = 0
        #         if summation > 0:
        #             test_row[combined_position] = 1


        #  This code choose only one best pair/list to cone within tests 'common_comp_2_tests'
        for common_comp, tests in common_comp_2_tests.items():
            best_score = 0
            winner_test = None
            for test in tests:
                if test_2_ordered_closest_comps[test][1] > best_score:
                    winner_test = test
                    best_score = test_2_ordered_closest_comps[test][1]
            comps_positions = test_2_ordered_closest_comps[winner_test][0]

            # insignificant
            normalized_score = best_score / float(len(self.metric_descriptor[winner_test]))
            print ("best pair score {}".format(normalized_score))
            if normalized_score < 0.05:
                continue

            suggested_omits = self.can_omit_comps(comps_positions, allready_omitted)
            if len(suggested_omits) == 1:
                continue
            elif len(suggested_omits) == 0:
                print ("Fatal - no comp representation for test ")
                continue
            self.actual_coned_positions.append(comps_positions)
            # first column will include all others
            combined_position = comps_positions[0]
            for test_row in matrix:
                summation = 0
                for comp in comps_positions:
                    summation += test_row[comp]
                    test_row[comp] = 0
                if summation > 0:
                    test_row[combined_position] = 1
            for test_components in tests_components:
                for to_omit in comps_positions[1:]:
                    try:
                        test_components.remove(to_omit)
                        allready_omitted.append(to_omit)
                    except ValueError:
                        pass

        for test, close_comps_positions in test_2_ordered_closest_comps.items():
            to_skip = False
            if close_comps_positions[0] is None:
                continue
            for close_comp in close_comps_positions[0]:
                if close_comp in common_comp_2_tests:
                    to_skip = True
            if to_skip:
                continue
            suggested_omits = self.can_omit_comps(close_comps_positions[0], allready_omitted)
            if len(suggested_omits) == 1:
                continue
            elif len(suggested_omits) == 0:
                print ("Fatal - no comp representation for test ", test)
                continue

            # insignificant score
            normalized_score = test_2_ordered_closest_comps[test][1] / float(len(self.metric_descriptor[test]))
            print ("best pair score {}".format(normalized_score))
            if normalized_score < 0.05:
                continue

            self.actual_coned_positions.append(close_comps_positions[0])
            # first column will include all others
            combined_position = close_comps_positions[0][0]
            for test_row in matrix:
                summation = 0
                for comp in close_comps_positions[0]:
                    summation += test_row[comp]
                    test_row[comp] = 0
                if summation > 0:
                    test_row[combined_position] = 1
            for test_components in tests_components:
                for to_omit in close_comps_positions[0][1:]:
                    try:
                        test_components.remove(to_omit)
                        allready_omitted.append(to_omit)
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

    def can_omit_comps(self, close_comps_positions, already_omitted):
        """

        :param close_comps_positions: list<int>
        :param already_omitted: list<int>
        :return: list of possible comps to omit
        """
        result = close_comps_positions[:]
        for comp in close_comps_positions:
            if comp in already_omitted:
                result.remove(comp)
        return result

    def calculate_common_close_comps_between_tests(self, test_2_ordered_closest_comps):
        """
        :param test_2_ordered_closest_comps: dict< test, (list<int>, score)>
        :return dictionary common comp to it's tests: dict<comp, list<test>>
        """
        temp = {}
        for test, ordered_closest_comps in test_2_ordered_closest_comps.items():
            ordered_comps = ordered_closest_comps[0]
            if ordered_comps is None:
                continue
            for comp in ordered_comps:
                if comp not in temp:
                    temp[comp] = [test]
                else:
                    temp[comp].append(test)
        result = {}
        for comp, tests in temp.items():
            if len(tests) > 1:
                result[comp] = tests
        return result


class JpeekDistanceComponentsMetric(ComponentsMetric):

    def __init__(self, regular_diagnose, metric_descriptor):
        metric_descriptor_new = {}
        for k,v in metric_descriptor.items():
            only_test = [i[0] for i in v]
            metric_descriptor_new[k] = only_test
        self.metric_descriptor_with_distance = metric_descriptor
        ComponentsMetric.__init__(self, regular_diagnose, metric_descriptor_new)
        # ComponentsMetric.__init__(self, regular_diagnose, metric_descriptor)
        self.sorted_comps_by_order = {}
        self.combined_position = None
        self.actual_coned_positions = []  # list<list<position>>
        print('init JpeekDistanceComponentsMetric')

    def change(self, matrix, tests_components):
        print('change JpeekDistanceComponentsMetric')
        self.original_matrix = [x[:] for x in matrix]
        for test, close_comps in self.metric_descriptor_with_distance.items(): # to change the input to new_metric_descriptor
            if close_comps:
                close_comps_positions, close_comps_score = self.calculate_closest_comps(close_comps)
                if close_comps_positions is not None:
                    close_comps_positions = self.order(close_comps_positions, test)
                self.test_2_ordered_closest_comps[test] = close_comps_positions, close_comps_score
        if len(self.test_2_ordered_closest_comps) > 0:
            self.combine_columns(self.test_2_ordered_closest_comps, matrix, tests_components)

            # test_index = self.context.initial_tests.index(test)

    def calculate_closest_comps(self, close_comps):
        """

        :param close_comps: list<ExtractedComponents>
        :return: list<int> , frequency score (for using in column combining)
        """
        try:
            close_comps = sorted(close_comps, key=lambda x:x[1])[::-1]
        except:
            print('sorted problem')
            print(close_comps)
        best_pair = close_comps[0][0].comps_positions
        best_score = close_comps[0][1]

        return  best_pair , best_score
        # connected_pairs_2_freq = {}
        # comp_position_2_freq = {}
        # max_pair_freq = 0
        # best_pair = None
        #
        # for close_comp in close_comps:
        #
        #     for pos in close_comp.comps_positions:
        #         if pos in comp_position_2_freq:
        #             comp_position_2_freq[pos] += 1
        #         else:
        #             comp_position_2_freq[pos] = 1
        #
        #     # self.comps_names = comps_names
        #     # self.comps_positions = comps_positions
        #     key = tuple(close_comp.comps_positions)
        #     if key in connected_pairs_2_freq:
        #         connected_pairs_2_freq[key] += 1
        #     else:
        #         connected_pairs_2_freq[key] = 1
        #     if max_pair_freq < connected_pairs_2_freq[key]:
        #         max_pair_freq = connected_pairs_2_freq[key]
        #         best_pair = key
        # if not best_pair:
        #     return None, None
        # best_pair_list = list(best_pair)
        # individual_max_freq = 0
        # for pos in best_pair_list:
        #     if comp_position_2_freq[pos] > individual_max_freq:
        #         individual_max_freq = comp_position_2_freq[pos]
        #
        # # print ("best pair {} score {}".format(best_pair_list, float(max_pair_freq + individual_max_freq) / len(close_comps)))
        # return best_pair_list, max_pair_freq + individual_max_freq

    def combine_columns(self, test_2_ordered_closest_comps, matrix, tests_components):
        """

        :param tests_components: list<int>
        :param test_2_ordered_closest_comps: dict< test, (list<int>, score)>
        :param matrix: list< list<int> >
        :return:
        """
        allready_omitted = []
        common_comp_2_tests = self.calculate_common_close_comps_between_tests(test_2_ordered_closest_comps)

        #  This code choose to cone more than 2 comps
        # if len(common_comp_2_tests) > 0:
        #     resulting_cone = []
        #     for common_comp, tests in common_comp_2_tests.items():
        #         for test in tests:
        #             for comp in test_2_ordered_closest_comps[test][0]:
        #                 if comp not in resulting_cone:
        #                     resulting_cone.append(comp)
        #
        #     self.actual_coned_positions.append(resulting_cone)
        #     # first column will include all others
        #     combined_position = resulting_cone[0]
        #     for test_row in matrix:
        #         summation = 0
        #         for comp in resulting_cone:
        #             summation += test_row[comp]
        #             test_row[comp] = 0
        #         if summation > 0:
        #             test_row[combined_position] = 1


        #  This code choose only one best pair/list to cone within tests 'common_comp_2_tests'
        for common_comp, tests in common_comp_2_tests.items():
            best_score = 0
            winner_test = None
            for test in tests:
                if test_2_ordered_closest_comps[test][1] > best_score:
                    winner_test = test
                    best_score = test_2_ordered_closest_comps[test][1]
            comps_positions = test_2_ordered_closest_comps[winner_test][0]

            # insignificant
            normalized_score = best_score# / float(len(self.metric_descriptor[winner_test]))
            # print ("best pair score {}".format(normalized_score))
            # if normalized_score < 0.05:
            #     continue

            suggested_omits = self.can_omit_comps(comps_positions, allready_omitted)
            if len(suggested_omits) == 1:
                continue
            elif len(suggested_omits) == 0:
                print ("Fatal - no comp representation for test ")
                continue
            self.actual_coned_positions.append(comps_positions)
            # first column will include all others
            combined_position = comps_positions[0]
            for test_row in matrix:
                summation = 0
                for comp in comps_positions:
                    summation += test_row[comp]
                    test_row[comp] = 0
                if summation > 0:
                    test_row[combined_position] = 1
            for test_components in tests_components:
                for to_omit in comps_positions[1:]:
                    try:
                        test_components.remove(to_omit)
                        allready_omitted.append(to_omit)
                    except ValueError:
                        pass

        for test, close_comps_positions in test_2_ordered_closest_comps.items():
            to_skip = False
            if close_comps_positions[0] is None:
                continue
            for close_comp in close_comps_positions[0]:
                if close_comp in common_comp_2_tests:
                    to_skip = True
            if to_skip:
                continue
            suggested_omits = self.can_omit_comps(close_comps_positions[0], allready_omitted)
            if len(suggested_omits) == 1:
                continue
            elif len(suggested_omits) == 0:
                print ("Fatal - no comp representation for test ", test)
                continue

            # insignificant score
            normalized_score = test_2_ordered_closest_comps[test][1] / float(len(self.metric_descriptor[test]))
            print ("best pair score {}".format(normalized_score))
            if normalized_score < 0.05:
                continue

            self.actual_coned_positions.append(close_comps_positions[0])
            # first column will include all others
            combined_position = close_comps_positions[0][0]
            for test_row in matrix:
                summation = 0
                for comp in close_comps_positions[0]:
                    summation += test_row[comp]
                    test_row[comp] = 0
                if summation > 0:
                    test_row[combined_position] = 1
            for test_components in tests_components:
                for to_omit in close_comps_positions[0][1:]:
                    try:
                        test_components.remove(to_omit)
                        allready_omitted.append(to_omit)
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

    def can_omit_comps(self, close_comps_positions, already_omitted):
        """

        :param close_comps_positions: list<int>
        :param already_omitted: list<int>
        :return: list of possible comps to omit
        """
        result = close_comps_positions[:]
        for comp in close_comps_positions:
            if comp in already_omitted:
                result.remove(comp)
        return result

    def calculate_common_close_comps_between_tests(self, test_2_ordered_closest_comps):
        """
        :param test_2_ordered_closest_comps: dict< test, (list<int>, score)>
        :return dictionary common comp to it's tests: dict<comp, list<test>>
        """
        temp = {}
        for test, ordered_closest_comps in test_2_ordered_closest_comps.items():
            ordered_comps = ordered_closest_comps[0]
            if ordered_comps is None:
                continue
            for comp in ordered_comps:
                if comp not in temp:
                    temp[comp] = [test]
                else:
                    temp[comp].append(test)
        result = {}
        for comp, tests in temp.items():
            if len(tests) > 1:
                result[comp] = tests
        return result