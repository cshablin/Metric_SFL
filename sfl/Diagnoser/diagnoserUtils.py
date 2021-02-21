from .ExperimentInstanceFactory import ExperimentInstanceFactory
from .FullMatrix import FullMatrix
from .Experiment_Data import Experiment_Data

__author__ = 'amir'

import csv
import json
from functools import reduce

def readPlanningFile(fileName, delimiter=";"):
    lines=open(fileName,"r").readlines()
    lines=[x.replace("\n","") for x in lines]
    sections=["[Description]", "[Components names]", "[Priors]","[Bugs]","[InitialTests]","[TestDetails]"]
    sections=[lines.index(x) for x in sections]
    description, components_names, priorsStr,BugsStr,InitialsStr,TestDetailsStr=tuple([lines[x[0]+1:x[1]] for x in zip(sections,sections[1:]+[len(lines)])])
    priors=eval(priorsStr[0])
    bugs=eval(BugsStr[0])
    initials=eval(InitialsStr[0])
    try:
        components = dict(map(lambda x: x if isinstance(x, tuple) else eval(x), eval(components_names[0].replace(delimiter, ','))))
    except:
        components = dict(eval(eval(components_names[0].replace(delimiter, ','))))
    testsPool={}
    estimatedTestsPool = {}
    error={}
    for td in TestDetailsStr:
        tup = tuple(td.split(delimiter))
        ind, actualTrace, err = None, None, None
        if len(tup) == 3:
            ind, actualTrace, err = tuple(td.split(delimiter))
        if len(tup) == 4:
            ind, actualTrace, estimatedTrace, err = tuple(td.split(delimiter))
            estimatedTestsPool[ind] = eval(estimatedTrace)
        actualTrace=eval(actualTrace)
        err=int(err)
        testsPool[ind] = actualTrace
        error[ind] = err
    Experiment_Data().set_values(priors, bugs, testsPool, components, estimatedTestsPool)
    return ExperimentInstanceFactory.get_experiment_instance(initials, error)



def write_planning_file(out_path,
                        bugs,
                        tests_details,
                        description="default description",
                        priors=None,
                        initial_tests=None,
                        delimiter=";"):
    """
    write a matrix to out path
    :param out_path: destination path to write the matrix
    :param bugs: list of bugged components
    :param tests_details: list of tuples of (name, trace, outcome).
     trace is set of components. outcome is 0 if test pass, 1 otherwise
    :param description: free text that describe the matrix. optional
    :param priors: map between components and priors probabilities of each component. optional
    :param initial_tests: list of tests for the initial matrix. optional
    :return:
    """
    # get the components names from the traces
    components_names = list(set(reduce(list.__add__, map(lambda details: details[1], tests_details), [])))
    map_component_id = dict(map(lambda x: tuple(reversed(x)), list(enumerate(components_names))))
    full_tests_details = []
    if len(tests_details[0]) == 3:
        for name, trace, outcome in tests_details:
            full_tests_details.append((name, sorted(list(map(lambda comp: map_component_id[comp] , trace), key=lambda x:x)), outcome))
    else:
        for name, trace, estimated_trace, outcome in tests_details:
            full_tests_details.append((name, sorted(list(map(lambda comp: map_component_id[comp] , trace), key=lambda x:x)), estimated_trace, outcome))
    if priors is None:
        priors = dict(((component, 0.1) for component in components_names))
    if initial_tests is None:
        initial_tests = list(map(lambda details: details[0], tests_details))
    bugged_components = [map_component_id[component] for component in filter(lambda c: any(list(map(lambda b: b in c, bugs)),components_names))]
    lines = [["[Description]"]] + [[description]]
    lines += [["[Components names]"]] + [list(enumerate(components_names))]
    lines += [["[Priors]"]] + [[[priors[component] for component in components_names]]]
    lines += [["[Bugs]"]] + [[bugged_components]]
    lines += [["[InitialTests]"]] + [[initial_tests]]
    lines += [["[TestDetails]"]] + full_tests_details
    with open(out_path, 'wb') as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerows(lines)

def write_planning_file_by_ei(out_path, ei):
    tests_details = list(map(lambda x: (x[0], map(Experiment_Data().COMPONENTS_NAMES.get, x[1]), ei.error[x[0]]),
                        Experiment_Data().POOL.items()))
    write_planning_file(out_path, ei.bugs, tests_details)

def write_merged_matrix(instance, out_matrix):
    componets = instance.get_components_vectors()
    similiar_componets = {}
    for component in componets:
        similiar_componets.setdefault(str(sorted(componets[component])), []).append(component)
    new_components_map = {}
    for comp in similiar_componets:
        candidates = similiar_componets[comp]
        new_name = "^".join(similiar_componets[comp])
        for candidate in candidates:
            new_components_map[candidate] = new_name
    get_name = lambda index: new_components_map.get(Experiment_Data().COMPONENTS_NAMES[index], Experiment_Data().COMPONENTS_NAMES[index])
    new_bugs = list(map(get_name, instance.bugs))
    new_pool = list(map(lambda test: [test, list(set(map(get_name, Experiment_Data().POOL[test]))), instance.error[test]], Experiment_Data().POOL))
    write_planning_file(out_matrix, new_bugs, new_pool)


def save_ds_to_matrix_file(ds, out_file):
    tests_details = list(map(lambda details: (
    str(details[0]), map(lambda c: Experiment_Data().COMPONENTS_NAMES[c], details[1]), details[2]),
                        list(zip(ds.tests_names, ds.TestsComponents, ds.error))))
    write_planning_file(out_file, list(map(lambda c: Experiment_Data().COMPONENTS_NAMES[c], Experiment_Data().BUGS), tests_details))


def read_json_planning_file(file_path):
    with open(file_path, "r") as f:
        instance = json.loads(f.read())
    return read_json_planning_instance(instance)


def read_json_planning_instance(instance):
    assert 'bugs' in instance,"bugs are not defined in planning_file"
    assert 'tests_details' in instance,"tests_details are not defined in planning_file"
    assert 'initial_tests' in instance,"initial_tests are not defined in planning_file"
    experiment_type = instance.get('experiment_type', None)
    testsPool = dict(map(lambda td: (td[0], td[1]), instance['tests_details']))
    error = dict(map(lambda td: (td[0], td[2]), instance['tests_details']))
    components = dict(instance['components_names'])
    estimatedTestsPool = instance.get('estimatedTestsPool', {})
    priors = instance.get('priors', [0.1 for _ in components])
    Experiment_Data().set_values(priors, instance['bugs'], testsPool, components, estimatedTestsPool)
    list(map(lambda x: setattr(Experiment_Data(), x[0], x[1]), instance.items()))
    return ExperimentInstanceFactory.get_experiment_instance(instance['initial_tests'], error, priors, list(map(lambda x: x.lower(), instance['bugs'])), testsPool, components, estimatedTestsPool, experiment_type)


def write_json_planning_file(out_path, tests_details, bugs=None, initial_tests=None, **kwargs):
    instance = dict()
    instance['bugs'] = bugs or Experiment_Data().BUGS
    components_names = list(set(reduce(list.__add__, map(lambda details: details[1], tests_details), [])))
    instance['components_names'] = list(enumerate(components_names))
    map_component_id = dict(map(lambda x: tuple(reversed(x)), list(enumerate(components_names))))
    full_tests_details = []
    for name, trace, outcome in tests_details:
        full_tests_details.append(
            (name, sorted(set(map(lambda comp: map_component_id[comp], trace)), key=lambda x: x), outcome))
    instance['tests_details'] = full_tests_details
    if initial_tests is None:
        initial_tests = list(map(lambda details: details[0], full_tests_details))
    instance['initial_tests'] = initial_tests
    instance.update(kwargs)
    with open(out_path, "wb") as f:
        json.dump(instance, f)

def write_json_planning_file_by_ei(out_path, ei, **kwargs):
    tests_details = list(map(lambda x: (x[0], map(Experiment_Data().COMPONENTS_NAMES.get, x[1]), ei.error[x[0]]), Experiment_Data().POOL.items()))
    write_json_planning_file(out_path, tests_details, **kwargs)
