from bicycle_track import BicycleTrack
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation


FANGSONG = matplotlib.font_manager.FontProperties(fname=r'C:\Windows\Fonts\simfang.ttf')
kw = {
	'fontsize':12, 
	'fontproperties':FANGSONG,
	'color': 'g'
}

def fx(t):
    return t

def fy(t):
    return 10-t**2/1.6

span = [-4, 4]
P0 = np.array([-8, 0])

# solve tracks
BT = BicycleTrack(fx, fy)
BT.solve(span, P0)

m = int(BT.X.shape[0]*0.9)
n = int(BT.X.shape[0]*0.1)
x0, y0, x1, y1 = BT.X[n], BT.Y[n], BT.FX[n], BT.FY[n]

with plt.xkcd():

	# full tracks in background
	BT.plot(plt,front_style='--', front_color='silver', back_style='-', back_color='silver')
	plt.text(-7, 6.6, '后轮轨迹参数方程：', **kw)
	plt.annotate(r"$x=x(t), y=y(t)$", 
		xy=(-4, 4), 
		xytext=(-7, 6), 
		arrowprops=dict(arrowstyle="->", connectionstyle='arc3,rad=0.5', color='c'), **kw)
	
	plt.annotate('前轮轨迹参数方程：', 
		xy=(3, 4), 
		xytext=(2, 2.5), 
		arrowprops=dict(arrowstyle="->", connectionstyle='arc3,rad=0.5', color='c'), **kw)
	plt.text(2, 2, r"$x=\alpha(t), y=\alpha(t)$", **kw)

	# a certain position
	plt.plot([x0, x1], [y0, y1], 'k')
	plt.plot([BT.X[m], BT.FX[m]], [BT.Y[m], BT.FY[m]], 'k')
	plt.plot([x0, x1], [y0, y1], 'ro')
	plt.plot([BT.X[m], BT.FX[m]], [BT.Y[m], BT.FY[m]], 'ro')

	plt.text(-6.3, 0.3, r'$P$', **kw)
	plt.text(-3.1, 4, r'$Q$', **kw)
	plt.annotate(r"$\overrightarrow{PQ}=(\alpha-x, \beta-y)$", 
		xy=((x0+x1)/2,(y0+y1)/2), 
		xytext=(-4, 1.5), 
		arrowprops=dict(arrowstyle="->", connectionstyle='arc3,rad=0.5', color='c'), **kw)
	plt.annotate(r"$\overrightarrow{\tau}=(x', y')$", 
		xy=(x0, y0), 
		xytext=(-8, 2.5), 
		arrowprops=dict(arrowstyle="->", connectionstyle='arc3,rad=0.5', color='c'), **kw)

	# text
	plt.text(-8, 9, r'$|\overrightarrow{PQ}|=L$', fontsize=15, color='r')
	plt.text(-8, 8, r'$\overrightarrow{PQ}\quad//\quad\overrightarrow{\tau}$', fontsize=15, color='r')
	plt.text(-4.8, 8.5, r'=>', fontsize=15, color='r')
	plt.text(-4, 9, r"$x'=\frac{x-\alpha}{L^2}[\alpha'(x-\alpha)+\beta'(y-\beta)]$", fontsize=15, color='r')
	plt.text(-4, 8, r"$y'=\frac{y-\beta}{L^2}[\alpha'(x-\alpha)+\beta'(y-\beta)]$", fontsize=15, color='r')
	

	plt.legend().remove()
	plt.show()
