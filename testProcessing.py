from multiprocessing import Pipe


def ct(c2):
    m = c2.recv()
    print(m)


c1, c2 = Pipe()

c1.send("Abc")
c1.send("Abcd")
ct(c2)





