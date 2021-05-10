
class ComponentsMetricType:
    def __init__(self):
        pass

    JavaCallGraphMetric = 1


class ComponentsMetric(object):

    def __init__(self, regular_diagnose, metric_descriptor):
        self.regular_diagnose = regular_diagnose
        self.metric_descriptor = metric_descriptor

    def change(self, matrix):
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

    def change(self, matrix):
        pass
