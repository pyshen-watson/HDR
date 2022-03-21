
class A:
    def __init__(self):
        self.a = 1

    def getB(self):
        print(A.__dict__)


a = A()
a.getB()