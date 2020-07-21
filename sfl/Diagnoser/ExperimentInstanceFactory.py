from .ExperimentInstance import ExperimentInstance
from .ExperimentInstanceInfluence import ExperimentInstanceInfluence
from .ExperimentInstanceOptimize import ExperimentInstanceOptimize
from .Diagnoser.Experiment_Data import Experiment_Data


class ExperimentInstanceFactory(object):

    @staticmethod
    def create_key(initial_tests, error):
        return repr(sorted(initial_tests)) + "-" + repr(
            sorted(map(lambda x: x[0], filter(lambda x: x[1] == 1, error.items()))))

    @staticmethod
    def get_experiment_instance(initials, error, experiment_type='normal'):
        classes = {'normal': ExperimentInstance,
                   'influence': ExperimentInstanceInfluence,
                   'optimize': ExperimentInstanceOptimize.Instances_Management().get_instance}
        return classes.get(experiment_type, classes['normal'])(initials, error)