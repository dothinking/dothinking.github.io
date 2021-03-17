---
layout: post
author: Train
description: frompyfunc()和vectorize()函数说明
keywords: numpy, Python, 数值计算
tags: [python, numeric analysis]
---

# NumPy库frompyfunc与vectorize的比较

---

NumPy提供了两种基本对象`ndarray`（n-dimensional array）和`ufunc`（universal function），后者指能够对数组中的每个元素进行操作的函数，可以提高运算速度。为了将普通的计算单个元素的函数转换成ufunc函数，NumPy提供了`frompyfunc()`和`vectorize()`两个函数。通过转换，可以使原来的函数参数接受向量输入（换句话说将转换后的函数的向量作为标量输入原来的函数），最终输出相应维度的结果。那么问题来了，

* 当我原来的函数本来就是输出数组，最终会输出新的二维数组么？

* 当我某些输入参数并不希望被向量化，那该怎么办？

本文针对应用中遇到的这两个问题作示例说明。

## 函数说明

参考Numpy官方手册对这两个函数的声明 [^1] [^2]：


    numpy.frompyfunc(func, nin, nout)
    class numpy.vectorize(pyfunc, otypes='', doc=None, excluded=None, cache=False)


* `frompyfunc()`的输入参数分别为函数名，输入参数个数，输出参数个数。
* `vectorize()`的输出参数较多，常使用的是前两个：函数名和返回类型。

并且注意文档中明确指出的一句话，`vectorize()`函数本质上是通过循环实现的，所以它的使用只是为了方便而不是效率。也就是说`frompyfunc()`更为底层些，效率相对更高。

## 问题一 函数返回数组

测试代码

    import numpy as np

    def test1(x):
        return x*np.array([0.0,1.0])

    fpf_test1 = np.frompyfunc(test1,1,1)
    vec_test1 = np.vectorize(test1)

    x = np.linspace(0,1,2)

测试结果

    print fpf_test1(x)
    [array([ 0.,  0.]) array([ 0.,  1.])]

    print vec_test1(x)
    ValueError: setting an array element with a sequence.

原函数输出结果也为一个数组，测试结果表明使用`frompyfunc()`函数达到了预期的效果，而`vectorize()`函数却导致了错误。

## 问题二 参数不需要向量化

测试代码

    import numpy as np

    def test2(x,y):
        '''返回x数组对应y位置的元素'''
        return x[int(y)]
    
    fpf_test2 = np.frompyfunc(test2,2,1)
    vec_test2 = np.vectorize(test2)
    
    x = np.linspace(0,4,5) * 10
    y = np.linspace(0,4,5)

测试结果

    print fpf_test2(x,y)
    TypeError: 'float' object has no attribute '__getitem__'

    print vec_test2(x,y)
    IndexError: invalid index to scalar variable.

    vec_test2.excluded.add(0) # 第一个参数无需向量化
    print vec_test2(x,y)
    [  0.  10.  20.  30.  40.]


结果可以看出，直接使用时由于将x也视为需要向量化处理的参数，所以都出现类型错误（x最终被视为一个标量了）。而使用`vectorize`函数类的`excluded`属性添加不考虑向量化的输入参数后，得到了正确的输出。


!!! warning "注意"
    `excluded`属性在`NumPy 1.7`之后版本才支持。不巧，我使用的是1.6版本，所以升级新版本后解决问题。

## 结论

`frompyfunc()`和`vectorize()`函数都可以使自定义的单输入值函数转为`ufunc`函数，但是注意以下几点：

* `frompyfunc()`较`vectorize()`有更高的执行效率，尤其在规模较大时。

* `frompyfunc()`可以适用于原函数输出数组的情形，而`vectorize()`则不支持。

* `vectorize()`可以指定不需要向量化处理的输入参数，从而满足具体需求。


[^1]: [numpy.frompyfunc](http://docs.scipy.org/doc/numpy/reference/generated/numpy.frompyfunc.html)
[^2]: [numpy.vectorize](http://docs.scipy.org/doc/numpy/reference/generated/numpy.vectorize.html#numpy.vectorize)