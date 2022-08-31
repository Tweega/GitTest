from operator import mul, add, truth
from functools import apply, reduce

apply_each = lambda fns, args=[]: map(apply, fns, [args]*len(fns))
bools = lambda lst: map(truth, lst)
bool_each = lambda fns, args=[]: bools(apply_each(fns, args))
conjoin = lambda fns, args=[]: reduce(mul, bool_each(fns, args))
all = lambda fns: lambda arg, fns=fns: conjoin(fns, (arg,))
both = lambda f,g: all((f,g))
all3 = lambda f,g,h: all((f,g,h))
and_ = lambda f,g: lambda x, f=f, g=g: f(x) and g(x)
disjoin = lambda fns, args=[]: reduce(add, bool_each(fns, args))
some = lambda fns: lambda arg, fns=fns: disjoin(fns, (arg,))
either = lambda f,g: some((f,g))
anyof3 = lambda f,g,h: some((f,g,h))
compose = lambda f,g: lambda x, f=f, g=g: f(g(x))
compose3 = lambda f,g,h: lambda x, f=f, g=g, h=h: f(g(h(x)))
ident = lambda x: x
not_ = lambda f: lambda x, f=f: not f(x)

#----- Some examples using higher-order functions -----#
# Don't nest filters, just produce func that does both
short_regvals = filter(both(shortline, isRegVal), lines)

# Don't multiply ad hoc functions, just describe need
regroot_lines = \
    filter(some([isRegDBRoot, isRegDBKey, isRegDBVal]), lines)

# Don't nest transformations, make one combined transform
capFlipNorm = compose3(upper, flip, normalize)
cap_flip_norms = map(capFlipNorm, lines)

 #*------ Limit nesting depth of map()/filter() ------#
intermed = filter(niceProperty, map(someTransform, lines))
final = map(otherTransform, intermed)

 #*------ Boolean algebra of composed functions ------#
satisfiedP = both(either(thisP,thatP), either(fooP,barP))


#*------ Use of a compositional Boolean function ------#
selected = filter(satisfiedP, lines)

