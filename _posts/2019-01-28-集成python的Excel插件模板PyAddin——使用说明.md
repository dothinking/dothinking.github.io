---
layout: post
author: Train
description: 使用python开发Excel插件
keywords: Python, vba
tags: [VBA, python]
---

虽然VBA是Excel的官配二次开发语言，但鉴于python的简洁易用高可维护性，相信不少人更倾向于使用python来处理Excel相关的二次开发工作。目前已有一些优秀的python第三方库，例如`xlrd`，`xlwt`和`xlutils`，可以分别实现Excel文件的读、写和读写转换工作；尤其推荐`xlwings`，可以如同VBA一样操作Excel工作簿、工作表、单元格区域等。这些库的一个共同特征是完全不依赖于Excel本身，仅仅将其作为一个对象进行处理。但有时候，我们还是限定在Excel环境下，只是希望借助python而不是VBA来处理数据。本文即介绍一个作者从实际需求中总结设计的Excel插件模板，实现VBA控制显示、python驱动计算的效果。

## 应用场景

对于开发者来说，利用开篇提及的python第三方库足以将任何繁杂的Excel数据处理工作转化为python编程来解决。但对于某些用户，他们已经习惯于在Excel环境下开展数据处理工作，并且系统通常没有配置而他们往往也不情愿安装python开发环境。此时如何使双方都达到舒适的状态——用户愉快地在Excel中使用开发者愉快地用python实现的功能？

- 基于Excel环境的限定，面向用户的只好是VBA控制的Excel插件

- 基于python开发且不依赖于系统配置python与否的目标，面向开发者的是便携式python

- 连接二者的桥梁是VBA与python的交互：VBA调用python脚本执行主要任务，然后获取其结果显示回Excel

综合起来即是本文介绍的Excel插件模板，暂且起名叫[`PyAddin`](https://github.com/dothinking/PyAddin)。


## 测试案例

1. 从[`PyAddin`](https://github.com/dothinking/PyAddin)克隆仓库或者下载文件，基本结构如下图所示：

<div align='center'><img src="{{ "/images/2019-01-28-01.jpg" | prepend: site.baseurl }}"></div>

2. 打开任意Excel文件，加载插件`pyAddin.xlam`（直接双击打开或者从`开发工具`->`Excel加载项`选择并加载）

<div align='center'><img src="{{ "/images/2019-01-28-02.jpg" | prepend: site.baseurl }}"></div>

以上自定义Ribbon菜单由`pyAddin.xlam`内置的XML文件和VBA控制，两个菜单项的响应函数如下所示：

```vba
Sub callback_cal(control As IRibbonControl)

    '''
    ' get value in cell A1, A2, then calculate A1/A2 in python
    '
    '''
    
    Dim a1$, a2$, args, res$
    
    a1 = ActiveSheet.Range("A1").Value
    a2 = ActiveSheet.Range("A2").Value
    
    args = Array(a1, a2)
    If RunPython("scripts.test.division", args, res) Then
        ActiveSheet.Range("A3").Value = res
    Else
        MsgBox res
    End If
    
End Sub


Sub callback_about(control As IRibbonControl)

    MsgBox "Shown with VBA, Driven by Python", vbOKOnly + vbInformation, "PyAddin 0.1"

End Sub
```

3. 在当前工作表`A1`、`A2`单元格输入内容，测试菜单按钮`A1/A2`的结果

从上一步可以看出VBA获取Excel数据，将其作为参数调用python脚本执行实际的工作，并获取其返回值进行相应的处理。`RunPython()`函数的第一个参数`"scripts.test.division"`指明了被调用的python方法——`scripts`包下的`test.py`模块的`dicision()`方法：

```python
@udf
def division(a, b):
    assert a!='', 'cell A1 is empty'
    assert b!='', 'cell A2 is empty'
    return float(a)/float(b)
```


## 自定义扩展

以下介绍自定义`PyAddin`插件模板以应用于具体案例的流程。

1. 自定义Ribbon菜单

解压`pyAddin.xlam`，修改其中的`\customUI\CustomUI.xml`文件。该文件决定了Ribbon菜单的显示内容及VBA回调函数的名称。

```xml
<customUI xmlns="http://schemas.microsoft.com/office/2006/01/customui">
  <ribbon startFromScratch="false">
    <tabs>
      <tab id="userRibbon" label="PyAddin">
        <group id="g1" label="My Test">
            <button id="btn_cal" 
              imageMso="Calculator" 
              size="large" 
              label="A1/A2" 
              onAction="callback_cal"/>
        </group>
          
        <group id="g2" label="About">
            <button id="btn_about" 
              imageMso="About" 
              size="large" 
              label="About" 
              onAction="callback_about"/>
        </group>
      </tab>
    </tabs>
  </ribbon>
</customUI>
```

`CustomUI.xml`文件结构已经很清晰了，`tab`、`group`和`button`分别对应了选项卡、分组和具体的菜单项，`button`的属性`imageMso`、`label`、`onAction`分别对应了菜单项的图标、显示内容和回调函数。具体可以参考：

> [Customizing the 2007 Office Fluent Ribbon for Developers (Part 2 of 3)](https://msdn.microsoft.com/en-us/library/aa338199(v=office.12).aspx)


2. 在VBA模块中定义回调函数

响应菜单点击事件的回调函数的基本格式为：

```vba
Sub callback_name(control As IRibbonControl)
    ...
    RunPython("package.module.method", args, res)
    ...
End Sub
```

函数体中使用`RunPython()`函数调用python脚本来处理具体事务，函数说明参考`pyAddin.xlam`的`general_function`模块： 

```vba
Function RunPython(method_name As String, args, ByRef res As String) As Boolean
    '''
    ' :param method_name: a string refer to the called python method -> package.module.method
    ' :param args: array for python arguments
    ' :param res: python return string
    ' :returns: True if everything is OK else False
    '
    '''
    pass
End Function
```

3. 在`scripts`文件夹下创建python脚本

推荐在`scripts`文件夹下创建python脚本，注意一个合法的python回调函数应该使用`@udf`装饰器。该装饰器保持VBA主调函数`RunPython()`与python脚本返回值的默认交互方式。

```python
# scripts/test.py
from .utility import udf

@udf
def user_function(*args):
    pass
```