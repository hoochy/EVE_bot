__author__ = 'hoochy'

def string_format(value):
    if type(value) == float:
        return "$%0.0f" % value
    elif type(value) == int:
        return "$%d" % value
    else:
        return "%s" % value

a = -10.0
print("dd " + a.__str__())
print(type(a))

b = 5
print(type(b))

f = ""
print(len(f))


gg = {'vanya' : 23323223, 'smith' : 32232332}
gg.
print(gg)
print(type(gg))