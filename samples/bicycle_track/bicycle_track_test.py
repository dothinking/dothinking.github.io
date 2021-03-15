import autograd.numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from bicycle_track import BicycleTrack


# front tyre track
def fx(t):
    return 5+5*np.cos(t)

def fy(t):
    return 5*np.sin(t)

fig = plt.figure(tight_layout=True)

L = 3
span = [-np.pi, np.pi]
colors = ['lightcoral', 'indianred', 'tomato']
front_track = None
back_tracks = []
bicycles = []

BT = BicycleTrack(fx, fy)
for i,c in enumerate(colors):
    theta = (i+1)*np.pi/2.0
    P0 = L*np.array([np.cos(theta), np.sin(theta)])
    BT.solve(span, P0)    

    # track data
    back_tracks.append((BT.X, BT.Y))    

    # plot track
    plt.plot(BT.X, BT.Y, color=c, label=r'back track with $\theta={0}\pi$'.format(theta/np.pi))

    # plot bicycle
    frame, = plt.plot([], [], 'k', linewidth=1)
    wheels, = plt.plot([], [], 'co')
    bicycles.append((frame, wheels))

front_track = (BT.FX, BT.FY)

# front track
plt.plot(*front_track, color='deepskyblue', label='front track')

# initial position
u = np.linspace(0, 2*np.pi, 50)
plt.plot(L*np.cos(u), L*np.sin(u), '--', color='silver', label='initial position')

# animation
def update_bicycle_pos(n, bicycles):
    ''' 
        Update bicycle position by setting new data.
    '''
    for track, (frame, wheel) in zip(back_tracks, bicycles):
        x1,y1,x,y = track[0][n], track[1][n], front_track[0][n], front_track[1][n]
        frame.set_data([x, x1], [y, y1])
        wheel.set_data([x, x1], [y, y1])
    return bicycles

ani = animation.FuncAnimation(fig, update_bicycle_pos, range(BT.t.shape[0]), fargs=(bicycles,), interval=100)

plt.legend(prop={'size':7})
plt.axis('equal')
plt.show()
