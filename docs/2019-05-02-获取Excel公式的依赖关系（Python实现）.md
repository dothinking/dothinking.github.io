---
layout: post
author: Train
description: 获取Excel中公式依赖的方法
keywords: python, win32com
tags: [python, VBA]
---

# 获取Excel公式的依赖关系（Python实现）

---

Excel中某个单元格的计算结果可以作为其他单元格计算公式的一部分，即二者存在依赖/引用的关系。尤其是对于复杂的表格，这种依赖关系可以方便我们追踪数据的相互作用。Excel已经在`Formula`->`Formula Auditing`组提供了可视化公式引用关系的功能：`Trace Precedents`和`Trace Dependents`，同时也可以通过相应的API来编程获取引用关系。本文即记录使用Python的`win32com`模块来实现之。

## 问题描述

假设几个单元格的公式如下：

```
## sheet1:
A1=1
B1=A1+1
B2=A1+2

## sheet2
B1=Sheet1!A1+1
B1=Sheet1!A1+2
```

显然`B1`的值依赖于`A1`，Excel中将`B1`称为`A1`的dependents，`A1`称为`B1`的Precedents。同理`B2`，以及sheet2中的`B1`、`B2`都是`A1`的Dependents；并且，`B1`和`B2`也可以有自己的Dependents。这样的话，`sheet1!B1`、`sheet1!B2`、`sheet2!B1`和`sheet2!B2`是`A1`的直接Dependents，而`sheet1!B1`、`sheet1!B2`、`sheet2!B1`和`sheet2!B2`的Dependents都是`A1`的间接Dependents。

在Excel中将光标定位到`A1`，然后点击`Formula`->`Formula Auditing`->`Trace Dependents`，会出现三个表示引用关系的箭头。其中两个实线箭头指向当前工作表内的两个引用`sheet1!B1`和`sheet1!B2`，虚线箭头指向其他工作表的引用即`sheet2!B1`和`sheet2!B2`。双击虚线箭头会出现`Go To`对话框，其中列出了`sheet2!B1`和`sheet2!B2`，选择相应记录即可跳转到目标位置。

`Trace Dependents`操作及其意义同理。

接下来，我们的问题是如何使用Python的`win32com`模块找出`A1`的所有Dependents。

## 准备工作

`win32com`模块是`pywin32`的一部分，因此在命令行运行下面指令进行安装

```
pip install pywin32
```

关于`win32com`操作Excel的基本代码可以参考

> [Python win32com模块操作Excel的几个应用（一）](2019-04-21-Python-win32com模块操作Excel的几个应用（一）.md)

> [Python win32com模块操作Excel的几个应用（二）](2019-09-13-Python-win32com模块操作Excel的几个应用（二）.md)


## 当前工作表内的引用

Excel`Range`对象的两个属性`precedents`和`dependents`记录了当前工作表范围内的依赖/引用关系，本例中

```
Range('A1').dependents = Range('B1'), Range('B2')
```

考虑到该属性不能在某个单元格不存在公式上的引用关系时使用，则可以组织Python代码如下：

```python
def get_direct_precedents(rng):
    '''get all precedents of current range from current sheet'''
    try:
        res = [x.address for x in rng.precedents]
    except Exception as e:
        res = []

    return res

def get_direct_dependents(rng):
    '''get all dependents of current range from current sheet'''
    try:
        res = [x.address for x in rng.dependents]
    except Exception as e:
        res = []

    return res
```


## 工作簿内的引用

本例中，如何才能获取到sheet2工作表中`B1`对sheet1中`A1`的引用关系呢？我们需要使用更一般的获取引用关系的函数`NavigateArrow` [^1]：

```
Range.NavigateArrow (TowardPrecedent, ArrowNumber, LinkNumber)
```

这个函数名称很形象，对应Excel中显示依赖/引用箭头的操作，其中，

- `TowardPrecedent`表示查找箭头的方向，`True`表示查找precedents，`False`表示查找dependents
- `ArrowNumber`表示箭头的序号，例如本例中有三个箭头，则依次取为1，2，3
- `LinkNumber`仅对工作表外引用有效，表示工作表外引用的序号。例如本例中的`sheet2!B1`和`sheet2!B2`，对应了序号1，2

这样的话，`Range('A1').NavigateArrow(False, 3, 2)`即表示`Sheet2!B2`。

`NavigateArrow`仅仅获取了直接引用，继续递归直接引用即可获取所有的间接引用了。结合此思路，参考代码如下：

```python
def get_all_dependents(xlApp, rng):
    '''get all dependents of current range from all worksheets'''
    # show dependents arrows first
    rng.ShowDependents()

    i, j = 0, 0
    res = set()
    while True:
        i += 1
        # navigate to next dependent:
        # - True -> precedents direction
        # - False -> dependent direction
        returnRange = rng.NavigateArrow(False, i)

        # if it's an external reference -> parent sheets are different
        if rng.Parent.Name != returnRange.Parent.Name:
            while returnRange:
                j += 1
                try:
                    returnRange = rng.NavigateArrow(False, i, j)
                    res.add((returnRange.Parent.Name, returnRange.address))
                    res |= get_all_dependents(xlApp, returnRange)
    
                except Exception as e:
                    # out of range: NavigateArrow method of Range class failed
                    returnRange = None   

        # if it's an internal reference
        else:
            # the last reference would be itself -> then stop the loop
            # for merged ranges, the last reference is the first cell
            if xlApp.Intersect(returnRange, rng):
                break

            res.add((returnRange.Parent.Name, returnRange.address))
            res |= get_all_dependents(xlApp, returnRange)

    return res
```

至此，主要内容已结束。对于引用关系复杂的工作簿，上述返回集合可能非常大，因此考虑生成器的版本：

```python
def get_all_dependents(xlApp, rng):
    '''get all dependents of current range from all worksheets'''
    # show dependents arrows first
    rng.ShowDependents()

    i, j = 0, 0
    while True:
        i += 1
        # navigate to next dependent:
        # - True -> precedents direction
        # - False -> dependent direction
        returnRange = rng.NavigateArrow(False, i)

        # if it's an external reference -> parent sheets are different
        if rng.Parent.Name != returnRange.Parent.Name:
            while returnRange:
                j += 1
                try:
                    returnRange = rng.NavigateArrow(False, i, j)
                    yield (returnRange.Parent.Name, returnRange.address)
                    # it does not work if just call this generator, 
                    # instead it should be iterated explicitly
                    # get_all_dependents(xlApp, returnRange)
                    for x in get_all_dependents(xlApp, returnRange):
                        yield x
                except Exception as e:
                    # out of range: NavigateArrow method of Range class failed
                    returnRange = None   

        # if it's an internal reference
        else:
            # the last reference would be itself -> then stop the loop
            # for merged ranges, the last reference is the first cell
            if xlApp.Intersect(returnRange, rng):
                break

            yield (returnRange.Parent.Name, returnRange.address)
            for x in get_all_dependents(xlApp, returnRange):
                yield x
```

`yield`关键字可以方便地将普通函数转为生成器，需要注意的是转换递归函数时，需要显式地迭代生成器，否则它不会自动计算下一个值。


[^1]: [Range.NavigateArrow method (Excel)](https://docs.microsoft.com/en-us/office/vba/api/Excel.Range.NavigateArrow)