---
layout: post
author: Train
description: 使用python开发Excel插件
keywords: Python, vba
tags: [VBA, python]
---

虽然VBA是Excel的官配二次开发语言，但鉴于python的简洁易用高可维护性，相信不少人更倾向于使用python来处理Excel相关的二次开发工作。目前已有一些优秀的python第三方库，例如`xlrd`，`xlwt`和`xlutils`，可以分别实现Excel文件的读、写和读写转换工作；尤其推荐`xlwings`，可以如同VBA一样操作Excel工作簿、工作表、单元格区域等。这些库的一个共同特征是完全不依赖于Excel本身，仅仅将其作为一个对象进行处理。但有时候，我们还是限定在Excel环境下，只是希望借助python而不是VBA来处理数据。本文即介绍一个作者从实际需求中总结设计的Excel插件模板设计工具[`pyAddin`](https://github.com/dothinking/PyAddin)，实现VBA控制显示、python驱动计算的效果。

## 主要功能

对于开发者来说，利用开篇提及的python第三方库足以将任何繁杂的Excel数据处理工作转化为python编程来解决。但对于某些用户，他们已经习惯于在Excel环境下开展数据处理工作，并且系统通常没有配置而他们往往也不情愿安装python开发环境。此时如何使双方都达到舒适的状态——用户愉快地在Excel中使用开发者愉快地用python实现的功能？

- **辅助开发者设计Excel插件**。根据开发者提供的插件Ribbon区域界面信息，例如分组、按钮名称、回调函数名称等，`pyAddin`自动生成一个插件框架，包含了预定义的菜单按钮及回调函数。开发者只需在相应的回调函数中填写具体业务代码即可。

- **连接VBA与Python**。`pyAddin`预定义了VBA与Python交互的接口函数，VBA调用python脚本执行主要任务，然后获取其结果显示回Excel。开发者可以设定Python解释器路径，因此可以内置便携式Python与插件一起发布给用户，这样便不依赖于用户系统配置Python开发环境与否。

## 安装与卸载

从[`pyAddin`](https://github.com/dothinking/PyAddin)克隆或者下载仓库，在仓库根目录下执行

```
python setup.py install
```

进行安装。或者以开发者方式安装，便于基于当前版本进行自定义的开发和修改:

```
python setup.py develop
```

安装完成后可以在命令行执行`pyAddin`命令查看基本使用方法：

```
usage: pyaddin [-h] [-n NAME] [-v] {init,create,update}

positional arguments:
  {init,create,update}  init, create, update

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  addin file name to be created/updated: [name].xlam
  -v, --vba             create VBA addin only, otherwise VBA-Python addin by
                        default
```

最后采用`pip`命令卸载即可：

```
pip uninstall pyaddin
```

## 使用方法

### 1. 新建空目录，初始化项目

```
D:\GitHub\PyAddin>mkdir examples
D:\GitHub\PyAddin>cd examples
D:\GitHub\PyAddin\examples>pyaddin init
```

当前`examples`目录下将产生一个Ribbon区域界面设计文件`customUI.yaml`。

### 2. 编辑`customUI.yaml`

Ribbon区域实际上由`XML`格式文件定义，`pyAddin`中将其简化为`YAML`格式文件`customUI.yaml`。参考基本注释设计插件内容即可，本文示例如下：

```yaml
# configuration for ribbom tab of Excel addin
# Examples:

PyAddin Test:
  GROUP_1:
    Cal_division:
      imageMso: Calculator
      size: large
      onAction: callback_cal
    Cal_multiply:
      imageMso: ~
      size: large
      onAction: callback_mtp
  HELP:
    About:
      imageMso: About
      size: large
      onAction: callback_about
```

表示创建名称为`PyAddin Test`的Ribbon工具卡，其中包含两个分组`GROUP_1`和`HELP`。第一个分组定义了两个按钮，并分别设定相应函数为`callback_cal()`和`callback_mtp()`。

### 3. 创建/更新插件

```
D:\GitHub\PyAddin\examples>pyaddin create --name my_first_addin
```

当前目录下将创建Excel插件`my_first_addin.xlam`及相应的辅助文件:

- `main.py`是VBA与Python交互的主函数，`main.py`将VBA请求发送到具体的Python脚本
- `main.cfg`为插件模板的配置文件，主要包括自定义Python解释器的路径
- `scripts`文件夹作为默认的Python脚本的保存位置


接下来转入下一步的具体业务逻辑的开发。在此过程中，如果需要增删新的功能菜单，可以回到第二步更新`customUI.yaml`，然后执行`update`命令：

```
D:\GitHub\PyAddin\examples>pyaddin update --name my_first_addin
```

这样可以在不影响原有代码的基础上，引入新添加的菜单回调函数模板。

### 4. 具体业务逻辑开发

以进行除法计算为例：在当前工作表`A1`、`A2`单元格输入内容，测试`A1/A2`的结果

#### 4.1 在VBA模块中定义回调函数

在菜单回调函数中使用VBA处理数据输入和输出，调用Python脚本完成具体的业务。

```vb
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
```

其中`RunPython()`函数调用Python脚本处理具体事务，函数说明参考插件的`general`模块： 

```vb
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


#### 4.2 在`scripts`文件夹下创建python脚本

从上一步可以看出`RunPython()`函数的第一个参数`"scripts.test.division"`指明了被调用的Python方法——`scripts`包下的`test.py`模块的`dicision()`方法，因此定义该方法如下：

```python
# scripts/test.py

def division(a, b):
    assert a!='', 'cell A1 is empty'
    assert b!='', 'cell A2 is empty'
    return float(a)/float(b)
```

如果使用的是内置的便携式Python，也可支持第三方库的安装和使用。默认情况下考虑减小体积，便携式Python并未预置`pip`。如果需要安装第三方库，可以先安装`pip`,然后`python -m pip install xxx`安装需要的库。最后发布给用户使用时，可以删除`pip`以减小体积，且不影响已经安装的库。

> [嵌入式Python : 如何在U盘安装绿色版 Python](https://baijiahao.baidu.com/s?id=1592976804446590381)
