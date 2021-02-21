# similarity measures
# each function recieves experiments instance and
# return sorted list of optional tests ordered by the chosen metric

import sfl.Diagnoser.ExperimentInstance
from functools import reduce


def get_min_vectors(test, diagnosis, is_boolean= False):
    # return two vectors the represents the test and diag.
    values = [False, True] if is_boolean else [0, 1]
    trace = .sfl.Diagnoser.ExperimentInstance.POOL[test]
    components = set(trace).union(set(diagnosis))
    vector = lambda l: [values[1] if c in l else values[0] for c in components]
    return vector(trace), vector(diagnosis)

def similarity_by_function(similarity_function, is_boolean=False):
    def similarity(ei):
        ei.diagnose()
        similarities = []
        optionals = ei.get_optionals_actions()
        for t in optionals:
            sim = 0.0
            diagnoesd_components = set(reduce(lambda d1,d2: d1 + d2.get_diag(), ei.diagnoses, []))
            for d in ei.diagnoses:
                t_vector, d_vector = get_min_vectors(t, d.get_diag(), is_boolean)
                try:
                    sim += d.get_prob() * similarity_function(t_vector, d_vector)
                except:
                    pass
            similarities.append(sim)
            # t_vector, d_vector = get_min_vectors(t, diagnoesd_components, is_boolean)
            # try:
            #     similarities.append(similarity_function(t_vector, d_vector))
            # except:
            #     similarities.append(0)
        return [x /sum(similarities) for x in similarities]
    return similarity

