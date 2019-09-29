'''
General process solving Ordinary Differential Equations, with solver like
forward Euler, Runge Kutta method. The step size is determined adaptively.

Combining ODEs:
    y1'=f1(x, y1, y2, ...yn)
    y2'=f2(x, y1, y2, ...yn)
    ...
    yn'=fn(x, y1, y2, ...yn)

with vector format:
    Y'=F(x, Y)

where:
    Y'=(y1', y2', ..., yn')
    F =(f1, f2, ..., fn)
    Y =(y1, y2, ..., yn)
'''

import numpy as np


def ode(F, span, Y0, solver=None, err=1e-6):
    '''
        General process solving ODEs Y'=F(x, Y) with adaptive step size.

        The initial point MUST exactly be the lower bound of span. If not, e.g. c1 <= t0 <= c2,
        range `span` should be split and solved separately, finally combine them together. Sample
        codes for c1 <= t0 <= c2:

            left = ode(F, [t0, c1], Y0, solver, err) # solving in a reversing direction, i.e. step size < 0
            right = ode(F, [t0, c2], Y0, solver, err)
            res = left[::-1] + right[1:]

        Arguments:
            F      : derivative function F(x, Y)
            span   : interval [x_start, x_end]
            Y0     : initial Y0 at x0=span[0] (can be a vector)
            err    : adaptive steps defined by numeric precision
            solver : solver function, e.g. Euler-forward, Runge-Kutta

        returns:
            A list of points:
                [(x_start,Y0), (x1,Y1), (x2,Y2),..., (x_end,Yn)]
    '''

    if solver==None: solver = Runge_Kutta4

    res = []
    x0, P0 = span[0], (span[0], Y0)
    res.append(P0)

    # if low bound is equal to upper bound, return itself
    h_max = span[1]-span[0] # initial step
    if h_max==0:
        return res    

    h = h_max
    while True:
        # get adaptive h
        h = adaptive_step(solver, F, P0, h, err)

        exceed = P0[0]+h>span[1] if h>0 else P0[0]+h<span[1]
        if exceed: break

        P1 = solver(F, P0, h)
        res.append(P1)
        P0 = P1 # preparation for next loop

    # close last point
    if P0[0]<span[1]:
        P1 = solver(F, P0, span[1]-P0[0])
        res.append(P1)

    return res


def adaptive_step(solver, F, P0, h0, err):
    '''
        Get step size adaptively

        Arguments:
            solver: function object of solving method
                        x, Y = solver(F, P, h)
            F     : derivative function F(x, Y)
            P0    : initial point (x0, Y0)
            h0    : initial step size
            err   : absolute err

        Return:
            step size
    '''
    assert h0!=0, "the step can't be zero!"
    h = h0

    # check diff between two tries of y1
    x1, Y11 = solver(F, P0, h)

    h = h/2.0
    P121 = solver(F, P0, h)
    x1, Y12 = solver(F, P121, h)

    if np.mean(abs(Y11-Y12))>err:
        # refine steps
        while np.mean(abs(Y11-Y12))>err:
            x1, Y11 = P121
            h = h/2
            P121 = solver(F, P0, h)
            x1, Y12 = solver(F, P121, h)            
    else:
        # expand steps
        h = h0
        while np.mean(abs(Y11-Y12))<err:
            x1, Y12 = solver(F, (x1, Y11), h)
            h = 2*h
            x1, Y11 = solver(F, P0, h)

        h = h/2.0 # previous step

    return h


def Runge_Kutta4(F, P0, h):
    '''
        Solving next point with 4 order Runge Kutta method.

        Arguments:
            F : function object return numpy.ndarry values of ODEs (f1, f2, ..., fn)
            P0: (x0, Y0) where Y0=(y10, y20, ..., yn0) is numpy.ndarry
            h : step size

        return:
            next point (x1, Y1)
    '''
    x0, Y0 = P0
    K1 = F(x0, Y0)
    K2 = F(x0+h/2, Y0+h*K1/2)
    K3 = F(x0+h/2, Y0+h*K2/2)
    K4 = F(x0+h, Y0+h*K3)
    Y1 = Y0 + h*(K1+2*K2+2*K3+K4)/6

    return (x0+h, Y1)


if __name__ == '__main__':
    
    import matplotlib.pyplot as plt

    # -------------------------------
    # test case 1: ODE
    # -------------------------------
    span = [0, 5]

    F = lambda x: np.sin(x**2) * np.exp(x)
    f = lambda x,y: 2*x*np.cos(x**2)*np.exp(x) + y

    res = ode(f, span, F(span[0]), err=1e-4)
    X,Y = zip(*res)
    X,Y = np.array(X), np.array(Y)

    plt.figure(tight_layout=True)
    plt.subplot(121)
    plt.plot(X, F(X), 'b')
    plt.plot(X, Y, 'o')


    # -------------------------------
    # test case 2: ODEs
    # -------------------------------
    span = [0, 2*np.pi]
    def F(x, Y):
        y1, y2 = Y
        return np.array([-np.sin(x), np.cos(x)])

    res = ode(F, span, np.array([0,0]), err=1e-6)    
    res = [x[1] for x in res]
    X,Y = zip(*res)
    X,Y = np.array(X), np.array(Y)

    plt.subplot(122)
    plt.plot(X, Y, 'o')
    plt.axis('equal')
    plt.show()

    
