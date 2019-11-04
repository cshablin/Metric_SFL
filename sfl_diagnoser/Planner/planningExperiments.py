__author__ = 'amir'

import csv
import functools
import gc
import glob
import os
import time
from threading import Thread
from numpy.random import choice

import Planner.lrtdp.LRTDPModule.Lrtdp
import Planner.mcts.main
import Planner.pomcp.main
from sfl_diagnoser.Planner.mcts.mcts import mcts_uct, clear_states

import HP_Random
import Planning_Results
import sfl_diagnoser.Diagnoser.diagnoserUtils
import sfl_diagnoser.Diagnoser.ExperimentInstance


def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]

            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception, e:
                    res[0] = e

            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception, je:
                print 'error starting thread'
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret

        return wrapper

    return deco


class Metrics(object):
    def __init__(self, ei, step):
        ei.diagnose()
        self.metrics = {"step": step}
        precision, recall = ei.calc_precision_recall()
        self.metrics["precision"] = precision
        self.metrics["recall"] = recall
        self.metrics["entropy"] = ei.entropy()
        self.metrics["max_probability"] = ei.getMaxProb()
        self.metrics["#_diagnoses"] = len(ei.diagnoses)

    def get_metrics(self):
        return self.metrics

    def add_time(self, total_time):
        self.metrics["total_time"] = total_time


class AbstractPlanner(object):
    def __init__(self):
        self.partial_metrics = dict()
        self.metrics = None

    # @timeout(3600)
    def plan(self, ei):
        # sfl_diagnoser.Diagnoser.ExperimentInstance.Instances_Management().clear()
        gc.collect()
        steps = 0
        start = time.time()
        self.partial_metrics[steps] = Metrics(ei, steps)
        while not self.stop_criteria(ei):
            gc.collect()
            ei = ei.addTests(self._plan(ei))
            steps += 1
            self.partial_metrics[steps] = Metrics(ei, steps).get_metrics()
        self.metrics = Metrics(ei, steps)
        self.metrics.add_time(time.time() - start)

    def stop_criteria(self, ei):
        PROBABILITY_STOP = 0.7
        ei.diagnose()
        return ei.getMaxProb() > PROBABILITY_STOP or len(ei.get_optionals_actions()) == 0

    def _plan(self, ei):
        return choice(ei.get_optionals_actions())

    def get_name(self):
        return self.__class__.__name__


class MCTSPlanner(AbstractPlanner):
    def __init__(self, approach, iterations):
        super(MCTSPlanner, self).__init__()
        self.approach, self.iterations = approach, iterations

    def plan(self, ei):
        clear_states()
        super(MCTSPlanner, self).plan(ei)

    def _plan(self, ei):
        action, weight = mcts_uct(ei, self.iterations, self.approach)
        return action

    def get_name(self):
        return "_".join(map(str, [self.__class__.__name__, self.approach, self.iterations]))


class InitialsPlanner(AbstractPlanner):
    def stop_criteria(self, ei):
        return True


class HPPlanner(AbstractPlanner):
    def _plan(self, ei):
        return ei.hp_next()


class LRTDPPlanner(AbstractPlanner):
    def __init__(self, approach="uniform", iterations=1, greedy_action_treshold=1, epsilon=0.001):
        super(LRTDPPlanner, self).__init__()
        self.approach = approach
        self.iterations = iterations
        self.greedy_action_treshold = greedy_action_treshold
        self.epsilon = epsilon

    def plan(self, ei):
        sfl_diagnoser.Planner.lrtdp.LRTDPModule.Lrtdp.clear_states()
        super(LRTDPPlanner, self).plan(ei)

    def _plan(self, ei):
        return sfl_diagnoser.Planner.lrtdp.LRTDPModule.Lrtdp(ei, epsilon=self.epsilon, iterations=self.iterations,
                                                             greedy_action_treshold=self.greedy_action_treshold, approach=self.approach)


class EntropyPlanner(AbstractPlanner):
    def __init__(self, threshold = 1.2, batch=1):
        super(EntropyPlanner, self).__init__()
        self.threshold = threshold
        self.batch = batch

    def _plan(self, ei):
        return ei.entropy_next(self.threshold, self.batch)


class ALLTestsPlanner(AbstractPlanner):
    def stop_criteria(self, ei):
        return len(ei.get_optionals_actions()) == 0


class PlannerExperiment(object):
    def __init__(self, planning_file):
        self.planning_file = planning_file
        self.planners = PlannerExperiment.get_planners()

    def experiment(self):
        for planner in self.planners:
            print planner.get_name()
            planner.plan(sfl_diagnoser.Diagnoser.diagnoserUtils.read_json_planning_file(self.planning_file))

    @staticmethod
    def get_planners():
        return [InitialsPlanner(), ALLTestsPlanner(), AbstractPlanner(), HPPlanner(), EntropyPlanner()] + \
               map(lambda x: MCTSPlanner("entropy", x), range(1, 20)) + map(lambda x: MCTSPlanner("entropy", x * 10), range(1, 20)) + \
               map(lambda x: MCTSPlanner("hp", x), range(1, 20)) + map(lambda x: MCTSPlanner("hp", x*10), range(1, 20))+ \
               map(lambda x: LRTDPPlanner("entropy", x), range(1, 20)) + map(lambda x: LRTDPPlanner("entropy", x * 10), range(1, 20)) + \
               map(lambda x: LRTDPPlanner("hp", x), range(1, 20)) + map(lambda x: LRTDPPlanner("hp", x*10), range(1, 20))


    def get_results(self):
        metrics = {}
        for planner in self.planners:
            metrics[planner.get_name()] = planner.metrics.metrics
        return metrics

    def get_partial_results(self):
        metrics = {}
        for planner in self.planners:
            metrics[planner.get_name()] = planner.partial_metrics
        return metrics

def mkOneDir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)


@timeout(3600)
def get_results_from_mdp(ei, alg):
    gc.collect()
    start = time.time()
    precision, recall, steps, rpr = alg(ei)
    total_time = time.time() - start
    return precision, recall, steps, total_time


def runAll_optimized(instancesDir, outDir, planners):
    outData = [["id", "planner", "tests", "precision", "recall", "steps", "time"]]
    outfile = os.path.join(outDir, "planningMED.csv")
    for matrix_id in os.listdir(instancesDir):
        ei = sfl_diagnoser.Diagnoser.diagnoserUtils.read_json_planning_file(os.path.join(instancesDir, matrix_id))
        for planner, alg in planners:
            try:
                precision, recall, steps, total_time, rpr = get_results_from_mdp(ei, alg)
                outData.append([matrix_id, planner, tests, precision, recall, steps, total_time])
                with open(outfile, "wb") as f:
                    writer = csv.writer(f)
                    writer.writerows(outData)
            except:
                pass


def mcts_by_approach(approach, iterations):
    def approached_mcts(ei):
        return Planner.mcts.main.main_mcts(ei, approach, iterations)

    return approached_mcts


def lrtdp_by_approach(epsilonArg, iterations, greedy_action_treshold, approachArg):
    def approached_lrtdp(ei):
        sfl_diagnoser.Planner.lrtdp.LRTDPModule.setVars(ei, epsilonArg, iterations, greedy_action_treshold, approachArg)
        return sfl_diagnoser.Planner.lrtdp.LRTDPModule.lrtdp()

    return approached_lrtdp


def entropy_by_threshold(threshold):
    return lambda ei: HP_Random.main_entropy(ei, threshold=threshold)


def entropy_by_batch(batch):
    return lambda ei: HP_Random.main_entropy(ei, batch=batch)


def planning_for_project(dir):
    for d in os.listdir(dir):
        if "." in d:
            continue
        if d == "weka":
            continue
        experiment_dir = os.path.join(dir, d)
        in_dir = os.path.join(experiment_dir, "planner")
        out_dir = os.path.join(experiment_dir, "all_planners")
        mkOneDir(out_dir)
        planners = [  # ("mcts_hp", mcts_by_approach("hp", 200)), ("mcts_entropy", mcts_by_approach("entropy", 200)),
            # ("lrtdp_hp", lrtdp_by_approach(0, 200, "hp")),
            ("mcts_hp_100", mcts_by_approach("hp", 100)),
            ("mcts_hp_70", mcts_by_approach("hp", 70)),
            ("mcts_hp_50", mcts_by_approach("hp", 50)),
            ("mcts_hp_10", mcts_by_approach("hp", 10)),
            ("mcts_hp_5", mcts_by_approach("hp", 5)),
            # ("lrtdp_entropy", lrtdp_by_approach(0, 200, "entropy")),
            # ("entropy_0.8", entropy_by_threshold(0.8)),
            # ("entropy_0.6", entropy_by_threshold(0.6)),
            # ("entropy_0.4", entropy_by_threshold(0.4)),
            # ("entropy_0.2", entropy_by_threshold(0.2)),
            # ("entropy_batch_2", entropy_by_batch(2)),
            # ("entropy_batch_5", entropy_by_batch(5)),
            ("HP", HP_Random.main_HP), ("entropy", HP_Random.main_entropy),
            ("Random", HP_Random.main_Random), ("initials", HP_Random.only_initials),
            ("all_tests", HP_Random.all_tests)]
        runAll_optimized(in_dir, out_dir, planners)


if __name__ == "__main__":
    pe = PlannerExperiment(r"C:\temp\47")
    pe.experiment()
    print pe.get_results()
