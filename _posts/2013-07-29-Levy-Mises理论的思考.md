---
layout: post
author: Train
description: "Levy-Mises理论假设条件的分析"
keywords: "Levy-Mises理论, 本构方程"
mathjax: true
---

增量理论指的是用应变增量描述本构关系，又称为流动理论。本构关系包括三部分：本构方程、屈服条件和硬化条件。

`Levy-Mises理论`是塑性成形增量理论之一，其基本假设如下：

> * 刚塑性材料  
> * Mises屈服准则  
> * 圣维南假设：加载瞬时，应力主轴与应变增量主轴重合  
> * 体积不变条件

## 推导过程

在圣维南假设的基础上，假设塑性应变增量的各个分量与相应偏应力分量成比例

$$d\varepsilon_{ij}^{p} = d\lambda\,{\sigma_{ij}}'$$

根据等效塑性应变增量$d{\bar\varepsilon}_{ij}^{p}$的定义式及体积不变条件得到

$$d{\bar\varepsilon}_{ij}^{p} = \sqrt{\frac{2}{3}\,d{\varepsilon'}_{ij}^{p}\,d{\varepsilon'}_{ij}^{p}} = \sqrt{\frac{2}{3}\,d{\varepsilon}_{ij}^{p}\,d{\varepsilon}_{ij}^{p}}$$

于是等效应变

$$\bar\sigma &= \sqrt{\dfrac{3}{2}\,{\sigma_{ij}}'\,{\sigma_{ij}}'} = \sqrt{\dfrac{3}{2}\,\dfrac{d\varepsilon_{ij}^{p}}{d\lambda} \, \dfrac{d\varepsilon_{ij}^{p}}{d\lambda}}&= \dfrac{1}{d\lambda}\,\sqrt{\dfrac{3}{2}\,d\varepsilon_{ij}^{p} \, d\varepsilon_{ij}^{p}}&= \dfrac{3}{2}\,\dfrac{1}{d\lambda}\,\sqrt{\dfrac{2}{3}\,d\varepsilon_{ij}^{p} \, d\varepsilon_{ij}^{p}}&= \dfrac{3}{2}\,\dfrac{1}{d\lambda}\,d{\bar\varepsilon}_{ij}^{p}$$

最后，根据Mises屈服条件$\bar\sigma = \sigma_s$得到

$$
d\lambda = \dfrac{3\,d{\bar\varepsilon}_{ij}^{p}}{2\,\bar\sigma} = \dfrac{3\,d{\bar\varepsilon}_{ij}^{p}}{2\,\sigma_s}
$$

## 疑问

### 理想刚塑性假设是否必要？

机械工业出版社的《材料成型原理》等资料在Livey-Mises理论的假设条件中都提到了理想刚塑性假设，那么理想刚塑性条件是必须的么？

理想刚塑性包含两层意思：

> * 材料变形特点为刚塑性，忽略材料的弹性变形，始终只有塑性应变  
> * 硬化模式为理想模式，即一旦屈服后流动应力不再增加

第一点是必须的，因为Livey-Mises理论确实没有考虑弹性变形；而第二点并没有涉及，也就是说，无论材料是何种硬化方式，本理论都是适用的。

### Mises屈服准则的假设条件是否必要？

从形式上看，前面推导过程中只是最后一步根据Mises屈服准则代入了$\bar\sigma=\sigma_s$，那么即便去除此条件，不是依然可以得到$d\lambda$的表达式$d\lambda = \dfrac{3\,d{\bar\varepsilon}_{ij}^{p}}{2\,\bar\sigma}$么？

那么，这个假设条件还是必要的么？

实际上，**我们常见的等效应力只是Mises等效应力习惯上的简称**。在不同的理论框架下，等效应力有不同的表达式。正是在Mises等效应力的定义下，才表现为：

$$\bar\sigma = f(\sigma'_{ij}) = \sqrt{\dfrac{3}{2}\,{\sigma_{ij}}'\,{\sigma_{ij}}'}$$

显然前面的推导过程是基于上式的，因此Mises屈服准则是Levy-Mises理论必须的假设条件之一。

> Mises屈服准则不仅给出了$\bar\sigma=\sigma_s$，还给出了Mises等效应力$\bar\sigma$的表达式。

### 屈服准则与本构方程的关联

进一步可以联想到屈服准则与本构方程是相互关联的，二者相互适应。以Livey-Mises理论为例，从塑性势的角度也可以推导出Livey-Mises理论所包含的本构方程

将以应力张量第二不变量描述的Mises屈服准则

$$f(\sigma'_{ij}) = {J'}_2-\frac{1}{3}\,\sigma_s^2=0$$

代入塑性势理论

$$d{\varepsilon'}_{ij}^{p} = d\lambda\,\frac{\partial\,f}{\partial\,{\sigma_{ij}}'}$$

得到

$$d{\varepsilon'}_{ij}^{p} &= d\lambda\,\frac{\partial\biggl({J'}_2-\frac{1}{3}\,\sigma_s^2\biggr)}{\partial\,{\sigma_{ij}}'}&= d\lambda\,\frac{\partial\biggl(\frac{1}{3}\,{\bar\sigma}^2\biggr)}{\partial\,{\sigma_{ij}}'}&= d\lambda\,{\sigma'}_{ij}$$

即得到与Livey-Mises理论同样的表达式。

由此可以体会：

> 本构方程描述的是物体的变形特性，具有普适意义；而一旦具体化其表达式（通常含有等效应力这个自变量），则与依赖于等效应力定义式的屈服准则有了关联。

## 总结

> Livey-Mises理论的假设中：理想硬化条件不是必要的，Mises屈服准则是必须的。  
>  本构方程与屈服条件因为等效应力的定义而统一于某种关系，例如能量原理（塑性势）  