'''
Test ode.py with Tractrix problem, a special case of Bike Track.

A bike with length a starts from an initial position:
front wheel (0, 0), rear wheel (a, 0), then it moves along the positive Y-axis.

The track of rear wheel is solved as:

y = a * arcsech(x/a) - sqrt(a^2-x^2)

'''

import numpy as np
import matplotlib.pyplot as plt
from ode import ode


a = 2

# theoretical solution
def F(x):
    return a*np.arccosh(a/x) - (a**2-x**2)**0.5

# derivative function of x,y components of rear wheel
def f(t, Y):
    y1, y2 = Y
    return np.array([(y2-t)*y1/a**2, (y2-t)**2/a**2])

span = [0, 10]
P0 = (0.0, np.array([a, 0]))
res = ode(f, span, P0, err=1e-6)

XY = [p[1] for p in res]
X,Y = zip(*XY)
X,Y = np.array(X), np.array(Y)

plt.figure(1)    
plt.plot(X, F(X), 'b') # thoretical solution
plt.plot(X, Y, 'o')    # ode solution
plt.xlim([0, a])
plt.ylim(1.1*np.array(span))
plt.show()