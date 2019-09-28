import autograd.numpy as np
from autograd import grad
from ode import ode


def Bike_trace(fw_x, fw_y, span, P0, L=1, err=1e-6):
    ''' 
        solve rear wheel trace according to front wheel trace and 
        initial position of the bicycle.

        The trace of front wheel is given by:
            x = fw_x(t)
            y = fw_y(t)

        Arguments:
            fw_x: function object of front wheel trace x component
            fw_y: function object of front wheel trace y component
            span: solving range of parameter t
            P0  : initial position of rear wheel (x, y) 
            L   : length of the bicycle -> distance between front wheel center
                    and rear wheel center

        Return:
            A list of solved points in given range:
                [(t0, (x0,y0)), (t1, (x1, y1)), ...]
    '''

    # initial point of front wheel
    t0 = span[0]
    Q0 = np.array([fw_x(t0), fw_y(t0)])
    assert np.sum((P0-Q0)**2)==L**2, "Invalid initial position of the rear wheel according to the bicycle length."

    # first derivative of front wheel x, y components
    dfx = grad(fw_x)
    dfy = grad(fw_y)

    # governing equation of the rear wheel trace
    def F(x, Y):
        y1, y2 = Y
        k = dfx(x)*(y1-fw_x(x)) + dfy(x)*(y2-fw_y(x))
        return k / L**2 * np.array([y1-fw_x(x), y2-fw_y(x)])

    # solving
    res = ode(F, span, (t0, P0), err=err)

    # parse x, y components
    t = np.array([P[0] for P in res])
    _ = [P[1] for P in res]

    X, Y = zip(*_)
    X, Y = np.array(X), np.array(Y)

    return t, X, Y


def Bike_trace_plot(plt, FX, FY, RX, RY, animation=None):
    ''' plot trace '''
    def update(num):
        bike.set_data(([FX[num], RX[num]], [FY[num], RY[num]]))
        return bike,  

    fig = plt.figure(tight_layout=True)
    plt.plot(FX, FY, 'b--')
    plt.plot(RX, RY, 'r--')
    plt.axis('equal')

    if animation:
        bike, = plt.plot([FX[0], RX[0]], [FY[0], RY[0]], 'black')
        ani = animation.FuncAnimation(fig, update, FX.shape[0]-1, interval=150, blit=True)
    else:
        ani = None

    return ani


if __name__ == '__main__':    

    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    def fx(x):
        return 5+5*np.cos(x)

    def fy(x):
        return 5*np.sin(x)

    L = 8
    span = [-np.pi, np.pi]
    P0 = np.array([-L, 0])

    # rear wheel trace
    t, X, Y = Bike_trace(fx, fy, span, P0, L, err=1e-6)

    # front wheel trace
    X1, Y1 = fx(t), fy(t)

    # plot
    ani = Bike_trace_plot(plt, X, Y, X1, Y1, animation)
    plt.show()