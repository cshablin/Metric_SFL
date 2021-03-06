__author__ = 'amir'


class Diagnosis(object):
    def __init__(self, diagnosis=None):
        if diagnosis is None:
            diagnosis = []
        self.diagnosis = sorted(diagnosis)
        self.probability = 0.0

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Diagnosis):
            if len(other.diagnosis) == len(self.diagnosis):
                return self.diagnosis == other.diagnosis
            else:
                for d in other.diagnosis:
                    if d not in self.diagnosis:
                        return False
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def clone(self):
        res = Diagnosis()
        res.diagnosis = list(self.diagnosis)
        res.probability = self.get_prob()
        return res

    def get_diag(self):
        return self.diagnosis

    def get_prob(self):
        return self.probability

    def set_probability(self, probability):
        self.probability = probability

    def set_from_tf(self, tf):
        # self.set_probability(tf.maximize())
        pass

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return str(sorted(self.diagnosis))+" P: "+str(self.get_prob())

    def as_dict(self):
        return {'_diagnosis': list(map(lambda f: {'_name': f}, sorted(self.get_diag()))), '_probability': self.get_prob()}
