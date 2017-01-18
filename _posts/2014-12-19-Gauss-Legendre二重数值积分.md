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

再如，`高斯积分公式`对积分点的选取采用了更高的要求——以积分点$x_0,x_1,\cdots,x_n$为零点的多项式$\omega_{n+1}(x)$满足：与任何次数不超过n的多项式$p_k(x)$带权正交。

相应的回报是：`n`阶高斯积分公式具有`2n+1`次代数精度。
 

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

选取不同的权系数及积分区间，可以得到不同的高斯型求积公式。`Legendre`多项式是区间$[-1,1]$，权函数为1时，$\lbrace 1,x,\cdots,x^n,\cdots\rbrace$正交化得到的多项式，因此其零点即为高斯积分点。同理，`Chebyshev`多项式的零点是另一类高斯型求积公式的积分点。

`Gauss-Legendre`求积公式表示为：

$$
\int_{-1}^{1} f(x) \mathrm{d}x \approx \sum_{k=0}^n A_k\,f(x_k)
$$
 
其中，$x_k$是n+1次`Legendre`多项式$P_n(x)$

$$
P_n(x) = \frac{1}{2^n\,n!}\,\frac{\mathrm{d}^n}{\mathrm{d}x^n}(x^2-1)^n \quad n=0,1,2,\cdots
$$

的零点。
 
`Gauss-Legendre`数值积分的思路同样为：求解积分点和积分系数，然后代入公式求和。

* 积分点可以通过求解`Legendre`多项式的零点得到，需要注意的是n阶`gauss-Legendre`公式的积分点是n+1阶`Legendre`多项式的零点。

* 根据定义，积分系数可以通过依次代入被积函数$x^k\,\,(k=0,1,2,\cdots,2n+1)$，求解代数方程组得到。然而，这样的方法较为复杂，一般推荐以下便于计算机计算的方法：

求解第$k$个积分系数$A_k$时，构造被积函数：

\begin{align\*}
f_k(x) &= \frac{(x-x_0)(x-x_1)\cdots(x-x_{k-1})(x-x_{k+1})\cdots(x-x_n)}{(x_k-x_0)(x_k-x_1)\cdots(x_k-x_{k-1})(x_k-x_{k+1})\cdots(x_k-x_n)} \\\\\\
&= \frac{\omega_{n+1}(x)}{(x-x_k)\,\omega'_{n+1}(x_k)}
\end{align\*}

显然该函数在$x_k$点的函数值为1，在其他积分点上的函数值为0，于是进行多项式积分就可以得到积分系数

$$
A_k = \sum_{k=0}^{n}A_k\,f(x_k) = \int_{a}^{b}f_k(x)\mathrm{d}x
$$

另外，需要通过换元，将`Legendre`多项式的标准积分区间$[-1,1]$转换到一般积分区间$[a,b]$：

$$
\int_{a}^{b}f(x)\mathrm{d}x = \frac{b-a}{2}\,\int_{-1}^{1}f\left(\frac{b-a}{2}\,t + \frac{b+a}{2}\right)\mathrm{d}t
$$

## Gauss-Legendre二重积分

以上是Gauss-Legendre数值积分的基本原理，对每个变量分别使用上述过程即可推广至一般区间上二重积分的计算。

\begin{align\*}
&\quad\int_a^b \\!\\! \int_{c(x)}^{d(x)}\,f(x,y)\mathrm{d}y\mathrm{d}x \\\\\\
&= \int_a^b\\!\\!\int_{-1}^{1}\,\frac{d(x)-c(x)}{2}\,f\left(x,\frac{d(x)-c(x)}{2}\,v + \frac{d(x)+c(x)}{2}\right)\mathrm{d}v\mathrm{d}x \\\\\\
&\approx \int_a^b \sum_{i=0}^n \left[A_i\,\frac{d(x)-c(x)}{2}\,f\left(x,\frac{d(x)-c(x)}{2}\,v_i + \frac{d(x)+c(x)}{2}\right)\right] \mathrm{d}x \\\\\\
&= \sum_{i=0}^n\left[A_i\int_a^b \alpha(x)\,f\left(x,\alpha(x)v_i+\beta(x)\right)\mathrm{d}x\right] \\\\\\
&= \sum_{i=0}^n\left[A_i\int_{-1}^1 \frac{b-a}{2} \alpha\left(\frac{b-a}{2}\,u + \frac{b+a}{2}\right)\,f\left(\frac{b-a}{2}\,u + \frac{b+a}{2},\alpha\left(\frac{b-a}{2}\,u + \frac{b+a}{2}\right)v_i+\beta\left(\frac{b-a}{2}\,u + \frac{b+a}{2}\right)\right)\mathrm{d}u\right] \\\\\\
&\approx \sum_{i=0}^n\left[A_i \sum_{j=0}^n A_j \frac{b-a}{2} \alpha\left(\frac{b-a}{2}\,u_j + \frac{b+a}{2}\right)\,f\left(\frac{b-a}{2}\,u_j + \frac{b+a}{2},\alpha\left(\frac{b-a}{2}\,u_j + \frac{b+a}{2}\right)v_i+\beta\left(\frac{b-a}{2}\,u_j + \frac{b+a}{2}\right)\right)\right] \\\\\\
&= \frac{b-a}{2}\,\sum_{i=0}^n\sum_{j=0}^n A_iA_j\alpha(U_j)f(U_j,V_{ji})
\end{align\*}

其中，

\begin{align\*}
\alpha(x) &= \frac{d(x)-c(x)}{2} \\\\\\
\beta(x) &= \frac{d(x)+c(x)}{2}
\end{align\*}

\begin{align\*}
U_j &= \frac{b-a}{2}\,u_j + \frac{b+a}{2} \\\\\\
V_{ji} &= \alpha(U_j)\,v_i + \beta(U_j)
\end{align\*}

## Matlab实现