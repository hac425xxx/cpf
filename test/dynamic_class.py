class A:
    def p(self):
        print "From A"


class B:
    def p(self):
        print "From B"


def k(c):
    a = c()
    a.p()


if __name__ == '__main__':
    k(A)
    k(B)
