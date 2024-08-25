class Main:
    main = 'main'

    def __init__(self, ip):
        self.ip = ip

class Sub1(Main):
    sub1 = 'sub1'

class Sub2(Main):
    sub2 = 'sub2'

class Sub3(Main):
    sub3 = 'sub3'

class Sub4(Main):
    sub4 = 'sub4'

class SubSub(Sub3):
    subSub = 'suBsub'


def test(*args):
    def wrapper(args):
        print(*args)
    wrapper(args)

print(test(('asdas',),('adddddad',), ('ddddd',)))