---
layout: post
author: Train
description: "Gauss-Legendre二重数值积分的推导和matlab实现"
keywords: "Matlab, 数值积分"
mathjax: true
---

数值积分一般都是机械求积，避开寻求原函数的困难，转为被积函数值的计算问题。对于插值型的求积公式，n阶积分（n+1个积分点）至少具有n阶代数精度。如果对插值节点的选取作出要求，则可进一步提高积分精度。

$$
\int_{a}^{b}f(x)\mathrm{d}x \approx \sum_{k=0}^{n}A_k\,f(x_k)
$$
 
例如，等距选取积分点则得到`牛顿-科斯特（Newton-Cotes）`公式。特别地，1，2阶的牛顿-科斯特公式分别是常用的`梯形公式`和`辛普森（Simpson）`公式。由于积分点作了等距的要求，作为回报，当阶数n为偶数时，牛顿-科斯特公式至少具有n+1次代数精度。

不过，当阶数较大（n$\ge$8）时，积分系数会出现负值，即计算不具有稳定性。所以又引进了复合求积公式——把积分区间划分为若干子区间，再在每个子区间采用低阶的求积公式。

再如，`高斯积分公式`对积分点的选取采用了更高的要求——以积分点$x_0,x_1,\cdots,x_n$为零点的多项式$\omega_{n+1}(x)$满足：与任何次数不超过n的多项式$p_k(x)$带权正交。相应的回报是：n阶高斯积分公式具有2n+1次代数精度。
 

$$
a \le x_0 \le x_1 \le \cdots \le x_n \le b
$$
$$
\omega_{n+1}(x) = (x-x_0)(x-x_1)\cdots(x-x_n)
$$
$$
p_k(x) = a_k x^k + a_{k-1} x^{k-1} + \cdots + a_0 \,\,\,(k \le n)
$$
$$
\int_{a}^{b}p_k(x) \omega_{n+1}(x) \rho(x) \mathrm{d}x = 0
$$


## Gauss-Legendre求积公式

选取不同的权系数及积分区间，可以得到不同的高斯型求积公式。`Legendre多项式`是区间$[-1,1]$，权函数为1时，$\{1,x,\cdots,x^n,\cdots\}$正交化得到的多项式，因此其零点即为高斯积分点。同理，`Chebyshev多项式`的零点是另一类高斯型求积公式的积分点。

Gauss-Legendre求积公式表示为：

$$
\int_{-1}^{1} f(x) \mathrm{d}x \approx \sum_{k=0}^n A_k\,f(x_k)
$$
 
其中，$x_k$是n+1次Legendre多项式P_n(x)

$$
P_n(x) = \frac{1}{2^n\,n!}\,\frac{\mathrm{d}^n}{\mathrm{d}x^n}(x^2-1)^n \quad n=0,1,2,\cdots
$$

的零点。
 
Gauss-Legendre数值积分的思路同样为：求解积分点和积分系数，然后代入公式求和。

* 积分点可以通过求解`Legendre多项式`的零点得到，需要注意的是n阶gauss-Legendre公式的积分点是n+1阶`Legendre多项式`的零点。

* 根据定义，积分系数可以通过依次代入被积函数$x^k\,\,(k=0,1,2,\cdots,2n+1)$，求解代数方程组得到。然而，这样的方法较为复杂，一般推荐以下便于计算机计算的方法：

求解第$k$个积分系数$A_k$时，构造被积函数：

\begin{align\*}
f_k(x) &= \frac{(x-x_0)(x-x_1)\cdots(x-x_{k-1})(x-x_{k+1})\cdots(x-x_n)}{(x_k-x_0)(x_k-x_1)\cdots(x_k-x_{k-1})(x_k-x_{k+1})\cdots(x_k-x_n)} \\\\\\
&= \frac{\omega_{n+1}(x)}{(x-x_k)\,\omega'_{n+1}(x_k)}
\end{align\*}

$$
f_k(x) = \frac{(x-x_0)(x-x_1)\cdots(x-x_{k-1})(x-x_{k+1})\cdots(x-x_n)}{(x_k-x_0)(x_k-x_1)\cdots(x_k-x_{k-1})(x_k-x_{k+1})\cdots(x_k-x_n)}
$$

显然该函数在$x_k$点的函数值为1，在其他积分点上的函数值为0，于是进行多项式积分就可以得到积分系数

$$
A_k = \sum_{k=0}^{n}A_k\,f(x_k) = \int_{a}^{b}f_k(x)\mathrm{d}x
$$

另一个重要问题是，一般积分区间为[a,b]，需要从[-1,1]进行变换
 
于是
 
实际上也对原始积分点做了同样的变换。


```matlab
function w = fun_gauss(f)
    x = [-sqrt(15)/5,0,sqrt(15)/5];y = x;
    [X,Y] = meshgrid(x,y);
    a = [5/9,8/9,5/9];b = a;
    [A,B] = meshgrid(a,b);
    w = sum(sum(A.*B.*f(X,Y)));
```

于是得到

$${W_0} = 4,\,{W_1} = 1.5188,\,{W_2} = 1.6234$$

## 单元离散后积分

为简单起见，将积分区域离散为$N=n^2$个面积相等的小区域，则每个单元的面积$\Delta S=\dfrac{4}{N}$。当单元$m$足够小时，可以以单元4个节点对应函数值的平均值来近似该单元区域内被积函数值，于是$W$可以表示为

\begin{align\*}
{W\_n} &= \sum\_{m=1}^{N}{\int\limits\_{y\_{m-1}}^{y\_m} {\int\limits\_{x\_{m-1}}^{x\_m} {f(x,\,y)\,\mathrm{d}x\mathrm{d}y}}} \\\\\\
&= \sum\limits\_{m=1}^{N}{\left[{\frac{1}{4}\sum\limits\_{i=1}^2 {\sum\limits\_{j=1}^2 {f(x\_i,\,y\_j)\,\Delta S}}} \right]} \\\\\\
&= \Delta S\,\sum\limits\_{m=1}^{N} {\sum\limits\_{i=1}^2 {\sum\limits\_{j=1}^2 {\frac{f(x\_i,\,y\_j)}{4}} } }
\end{align\*}

其中$x_1,\,x_2$为单元$m$的节点的两个横坐标。 

<div align='center'><img src="{{ "/images/2014-11-28-01.png" | prepend: site.baseurl }}"></div>

上式可以理解为将区域离散后，每个单元的每个节点都为最终的积分值贡献1/4的作用。单从节点来看，内层节点贡献为1，边界节点（除4个角节点外）贡献1/2，4个角节点贡献1/4。这很容易通过Matlab编程实现，代码如下：

```matlab
function w = fun_trapezoid(n,f)
    [X,Y] = meshgrid(linspace(-1,1,n));
    a = f(X(2:n-1,2:n-1),Y(2:n-1,2:n-1));
    b = f(X(1,:),Y(1,:))+f(X(n,:),Y(n,:));
    c = f(X(:,1),Y(:,1))+f(X(:,n),Y(:,n));
    d = f(X(1,1),Y(1,1))+f(X(1,n),Y(1,n))+f(X(n,1),Y(n,1))+f(X(n,n),Y(n,n));
    t = sum(sum(a)) + sum(b)/2 + sum(c)/2 - d/4;
    w = 4*t/n^2;
```

于是得到

$${W_{10}} = 1.2865,\,{W_{100}} = 1.5886,\,{W_{5000}} = 1.6205$$

这样的积分结果差强人意，单元数达到`5000×5000`才勉强保证小数点后2位精度。

为了改善精度，在子域上使用Simpson求积公式，得到

\begin{align\*}
{W\_n} &= \sum\_{m=1}^{N}{\int\limits\_{y\_{m-1}}^{y\_m} {\int\limits\_{x\_{m-1}}^{x\_m} {f(x,\,y)\,\mathrm{d}x\mathrm{d}y}}} \\\\\\
&= \sum\limits\_{m=1}^{N}{\left[{\frac{1}{36}\sum\limits\_{i=1}^3 {\sum\limits\_{j=1}^3 {A\_i\,A\_j\,f(x\_i,\,y\_j)\,\Delta S}}} \right]} \\\\\\
&= \dfrac{\Delta S}{36}\,\sum\limits\_{m=1}^{N} {\sum\limits\_{i=1}^3 {\sum\limits\_{j=1}^3 {A\_i\,A\_j\,f(x\_i,\,y\_j)} } }
\end{align\*}

其中$x_1,\,x_2,\,x_3$分别为单元$m$边界的三个等分点的横坐标。$A=[1,4,1]$为积分系数。 

<div align='center'><img src="{{ "/images/2014-11-28-02.png" | prepend: site.baseurl }}"></div>

 Matlab代码为

```matlab
function w = fun_simpson(n,f)
    t = 2/n;
    [A,B] = meshgrid([1,4,1],[1,4,1]);
    w = 0.0;
    for i = 0:n^2-1
        x = mod(i,n);
        y = floor(i/n);    
        x = -1 + x*t;
        y = -1 + y*t;
        [X,Y] = meshgrid(linspace(x,x+t,3),linspace(y,y+t,3));
        w = w + sum(sum(A.*B.*f(X,Y)/(3*n)^2));
    end
```

最终计算结果为

$${W_2} = 1.6285,\,{W_5} = 1.6213,\,{W_{10}} = 1.6211$$

## 总结

高斯积分以积分点的计算为代价可以在较少积分点的情况下获得一定的精度，而离散积分的方法以离散单元数为代价来提高精度；但是精度会因为子域上选取的积分方式的不同而表现出较大的差异：只有单元节点参与计算时，精度相对较低；当单元边界中点也加入计算，精度得以大幅度提高。

区域离散后积分的方法本质上是复化求积法。通过划分子区间并在子区间上使用低阶求积公式来提高精度并兼顾计算复杂程度。第一种求积方法是梯形公式，第二种是精度更高的Simpson公式（即2阶Newton-Cotes公式）。这种方法的优势在于当积分区域极不规则时，可以通过离散的方法在子区间上进行积分并最终累加。例如实际三维成形问题，由于积分区域无法直接写成显式的积分上下限形式，因此也无法直接在全域上使用高斯求积公式。

综合来看，在上限法分析模型中，一般二维即平面应变或轴对称模型的积分区域是规则的，因此高斯积分法相对更有应用优势；而三维问题变形区通常较为复杂，离散求积的方法更具优势，且离散区域上的Simpson公式也可以保证精度。