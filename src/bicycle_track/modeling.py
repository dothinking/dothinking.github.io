from BicycleTrack import BicycleTrack
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

font_name = "STKaiti"
matplotlib.rcParams['font.family']=font_name
matplotlib.rcParams['axes.unicode_minus']=False # in case minus sign is shown as box

def fx(t):
    return t

def fy(t):
    return 10-t**2/1.6

span = [-4, 4]
P0 = np.array([-8, 0])

# solve tracks
BT = BicycleTrack(fx, fy)
BT.solve(span, P0)

n = int(BT.X.shape[0]*0.1)
x0, y0, x1, y1 = BT.X[n], BT.Y[n], BT.FX[n], BT.FY[n]

with plt.xkcd():
	# full tracks in background
	BT.plot(plt,front_style='--', front_color='silver', back_style='-', back_color='silver')
	plt.annotate("后轮参数方程：$x=x(t), y=y(t)$", 
		fontsize=10,
		xy=(-4, 4), 
		xytext=(-7, 6), 
		arrowprops=dict(arrowstyle="->", connectionstyle='arc3,rad=0.5', color='c'))
	plt.annotate(r"前轮参数方程：$x=\alpha(t), y=\alpha(t)$", 
		fontsize=10,
		xy=(3, 4), 
		xytext=(2, 2), 
		arrowprops=dict(arrowstyle="->", connectionstyle='arc3,rad=0.5', color='c'))

	# a certain position
	plt.plot([x0, x1], [y0, y1], 'k')
	plt.plot([x0, x1], [y0, y1], 'ro')
	plt.text(x0-1, y0+0.5, r'$P\left(x(t), y(t)\right)$', fontsize=10)
	plt.text(x1, y1+0.5, r'$Q\left(\alpha(t), \beta(t)\right)$', fontsize=10)
	plt.annotate("$L$", 
		fontsize=10,
		xy=((x0+x1)/2,(y0+y1)/2), 
		xytext=((x0+x1)/2-2,(y0+y1)/2+2), 
		arrowprops=dict(arrowstyle="->", connectionstyle='arc3,rad=0.5', color='c'))

	# vector
	plt.annotate("O", xy=(x0,y0), xytext=(0,0), arrowprops=dict(arrowstyle="->"), fontsize=10)
	plt.annotate("", xy=(x1,y1), xytext=(0,0), arrowprops=dict(arrowstyle="->"))

	# text
	plt.text(0, 8, r'$|PQ|=L$', fontsize=10)
	plt.text(0, 7, r'$\overrightarrow{OP}+\overrightarrow{PQ}=\overrightarrow{OQ}$', fontsize=10)

	plt.legend().remove()
	plt.show()
