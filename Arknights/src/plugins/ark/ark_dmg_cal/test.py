class Test_class(object):
    def __init__(self):
        names = self.__dict__
        for i in range(6):
            names["n" + str(i)] = i
            # names['x%s' % i] = i


t = Test_class()
print(t.n0, t.n1, t.n2, t.n3, t.n4, t.n5)
