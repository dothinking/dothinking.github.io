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


def ode(F, span, P0, solver=None, err=1e-6):
    '''
        Adaptive Runge-Kutta method for ODEs Y'=F(x, Y)

        :param F      : derivative function F(x, Y)
        :param span   : interval [x_start, x_end]
        :param P0     : initial point (x0, Y0). x0 may out of range `span`
        :param err    : adaptive steps defined by numeric precision
        :returns      : [(x_start,Y0), (x1,Y1), (x2,Y2),..., (x_end,Yn)]
    '''

    if solver==None: solver = Runge_Kutta4

    x0, Y0 = P0
    c1, c2 = span

    # check
    assert c2>c1, 'range [{0}, {1}] MUST in ascend order'.format(c1, c2)

    # starts from x0 tp c1, return results in range [c1, c2]
    if x0 < c1:
        left = ode_solving(F, [x0, c1], Y0, solver, err)
        right = ode_solving(F, [c1, c2], left[-1][1], solver, err)
        return right

    # x0 -> c1 in reverse order and x0 -> c2
    elif c1 <= x0 <= c2:
        left = ode_solving(F, [x0, c1], Y0, solver, err)
        right = ode_solving(F, [x0, c2], Y0, solver, err)
        return left[::-1] + right[1:]

    # starts from x0 to c2 in reverse order, return results in range [c1, c2]
    else:
        left = ode_solving(F, [x0, c2], Y0, solver, err)
        right = ode_solving(F, [c2, c1], left[-1][1], solver, err)
        return right[::-1]


def ode_solving(F, span, Y0, solver=None, err=1e-6):
    '''
        General process solving ODEs Y'=F(x, Y) with adaptive step size

        Arguments:
            F      : derivative function F(x, Y)
            span   : interval [x_start, x_end]
            Y0     : initial Y0 at x0=span[0]
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
    
    import numpy as np
    import matplotlib.pyplot as plt

    span = [0, 5]
    x0 = 2

    F = lambda x: np.sin(x**2) * np.exp(x)
    f = lambda x,y: 2*x*np.cos(x**2)*np.exp(x) + y

    res = ode(f, span, [x0, F(x0)], err=1e-4)
    X,Y = zip(*res)
    X,Y = np.array(X), np.array(Y)

    plt.figure(1)
    plt.plot(X, F(X), 'b')
    plt.plot(X, Y, 'o')
    plt.plot(x0, F(x0), 'r^')
    plt.show()