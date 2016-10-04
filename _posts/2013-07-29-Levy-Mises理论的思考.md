---
layout: post
author: Train
description: "Levy-Mises理论假设条件的分析"
keywords: "Levy-Mises理论, 本构方程"
mathjax: true
---

Levy-Mises是塑性成形增量理论之一。增量理论指用应变增量描述本构关系，又称为流动理论。本构关系包括三部分：本构方程、屈服条件和硬化条件。

## 前提假设

Levy-Mises理论基于如下假设：

> * 刚塑性材料  
> * Mises屈服准则  
> * 圣维南假设：加载瞬时，应力主轴与应变增量主轴重合  
> * 体积不变条件


## 推导过程

在圣维南假设的基础上，假设等效塑性应变增量的各个分量与相应偏应力分量成比例

$$d\varepsilon_{ij}^{p} = d\lambda\,{\sigma_{ij}}'$$

根据等效塑性应变增量定义式及体积不变条件得到

$$d\bar{\varepsilon}_{ij}^{p} = \sqrt{\dfrac{2}{3}\,d{{\varepsilon}'}_{ij}^{p}\,d{{\varepsilon}'}_{ij}^{p}} = \sqrt{\dfrac{2}{3}\,d{\varepsilon}_{ij}^{p}\,d{\varepsilon}_{ij}^{p}}$$

根据屈服条件

$$\bar\sigma = \sqrt{\dfrac{3}{2}\,{\sigma_{ij}}'\,{\sigma_{ij}}'} = \sigma_s$$



则



sans-serif;"> 疑问</span></span></h1>
<h2> 需要做理想刚塑性假设么？</h2>
一些资料在Livey-Mises理论的假设条件中都提到理想刚塑性假设，例如我本科时的教材《材料成型原理》（机械工业出版社），还有网上的<a href="http://jpkc.hfut.edu.cn/jpkc2004/2004/cxyn/kejian/shang/ch17_03.htm">一些教程、课件</a>，那么理想刚塑性条件是必须的么？

理想刚塑性包含两层意思：
<ul>
    <li>材料变形特点为刚塑性，忽略材料的弹性变形，始终只有塑性应变</li>
    <li>硬化模式为理想模式，即一旦屈服后流动应力不再增加</li>
</ul>
分析这两点，第一点是必须的，因为这个理论确实没有考虑弹性变形，而第二点并没有涉及，也就是说，无论材料是何种硬化方式，本理论都是适用的。
<h2>Mises屈服准则的假设条件是必须的么？</h2>
参考推导部分，由Mises屈服准则

<span class="Apple-style-span" style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;"><img class="wp-image-542 aligncenter" style="border-style: initial; border-color: initial; margin-top: 0.4em;" src="http://127.0.0.3/wordpress//wp-content/uploads/2013/07/2013-07-29_231118.jpg" alt="2013-07-29_231118" width="108" height="48" /></span>

最终得到
<p style="text-align: center;"><img class=" wp-image-543 aligncenter" style="border-style: initial; border-color: initial;" src="http://127.0.0.3/wordpress//wp-content/uploads/2013/07/2013-07-29_231149-300x110.jpg" alt="2013-07-29_231149" width="240" height="88" /></p>
那么假如去掉屈服准则的假设条件，不是依然可以得到如下的结论嘛
<p style="text-align: center;"><img class="wp-image-544 aligncenter" style="border-style: initial; border-color: initial;" src="http://127.0.0.3/wordpress//wp-content/uploads/2013/07/2013-07-29_231207.jpg" alt="2013-07-29_231207" width="151" height="85" /></p>
那么，这个假设条件还是必要的么？

事实上并不是这样子。

产生这种偏差理解的根源在于，对Mises屈服准则的认识仅限于
<p style="text-align: center;"><img class="aligncenter" style="border-style: initial; border-color: initial;" src="http://127.0.0.3/wordpress//wp-content/uploads/2013/07/2013-07-29_231118.jpg" alt="2013-07-29_231118" width="108" height="48" /></p>
<p style="text-align: left;">其实我们常见的等效应力只是Mises等效应力习惯上的简称，等效应力可以根据不同的定义有不同的形式，例如</p>
<p style="text-align: center;"><img class="wp-image-546 aligncenter" style="border-style: initial; border-color: initial;" src="http://127.0.0.3/wordpress//wp-content/uploads/2013/07/2013-07-29_231409-300x75.jpg" alt="2013-07-29_231409" width="270" height="68" /></p>
<p style="text-align: left;">只是在Mises等效应力的定义下才有：</p>
<p style="text-align: center;"><img class=" wp-image-545 aligncenter" style="border-style: initial; border-color: initial;" src="http://127.0.0.3/wordpress//wp-content/uploads/2013/07/2013-07-29_231306-300x103.jpg" alt="2013-07-29_231306" width="270" height="93" /></p>
<p style="text-align: left;">而在之前的推导部分已经用到了</p>
<p style="text-align: left;"><img class=" wp-image-550 aligncenter" style="border-style: initial; border-color: initial;" src="http://127.0.0.3/wordpress//wp-content/uploads/2013/07/2013-07-29_233742.jpg" alt="2013-07-29_233742" width="180" height="95" />所以Mises屈服准则是Levy-Mises理论必须的假设条件之一。</p>

<h2 style="text-align: left;">屈服准则与本构方程的关联</h2>
<p style="text-align: left;">更进一步，可以联想到屈服准则与本构方程是由关联的，二者相互适应。以Livey-Mises理论为例，从塑性势的角度也可以推导出Livey-Mises理论所包含的本构关系。</p>
<p style="text-align: left;">根据塑性势理论，</p>
<p style="text-align: center;"><img class=" wp-image-547 aligncenter" style="border-style: initial; border-color: initial;" src="http://127.0.0.3/wordpress//wp-content/uploads/2013/07/2013-07-29_231636.jpg" alt="2013-07-29_231636" width="200" height="84" /></p>
<p style="text-align: left;">采用以应力张量第二不变量描述的Mises屈服准则</p>
<p style="text-align: center;"><img class=" wp-image-548 aligncenter" style="border-style: initial; border-color: initial;" src="http://127.0.0.3/wordpress//wp-content/uploads/2013/07/2013-07-29_231752-300x91.jpg" alt="2013-07-29_231752" width="240" height="73" /></p>
<p style="text-align: left;">代入塑性势表达式中得到，</p>
<p style="text-align: center;"><img class="wp-image-549 aligncenter" style="border-style: initial; border-color: initial;" src="http://127.0.0.3/wordpress//wp-content/uploads/2013/07/2013-07-29_232317.jpg" alt="2013-07-29_232317" width="1062" height="190" /></p>
即得到Livey-Mises理论同样的表达式。

由此可以体会：

本构方程描述的是物体的变形特性，具有普适的意义；而一旦具体化其表达式（通常含有等效应力这个自变量），则与也依赖于等效应力的定义的屈服准则有了关联性。
<h1>总结</h1>
<blockquote>
<ul>
    <li>Livey-Mises理论的假设条件</li>
    <li>理想硬化条件不是Livey-Mises理论所必须的假设条件</li>
    <li>Mises屈服准则是Livey-Mises理论必须的假设条件</li>
    <li>本构方程与屈服条件因为等效应力的定义而统一于某种关系，例如能量原理（塑性势）。</li>
</ul>
</blockquote>
&nbsp;
<div class="download">
<div>本文公式文件：Livey-Mises理论的思考</div>
&nbsp;

</div>