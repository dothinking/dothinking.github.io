---
layout: post
author: Train
description: 使用python开发Excel插件
keywords: Python, vba
tags: [VBA, python]
---

`PyAddin`是一个Excel插件模板，方便在VBA中调用python脚本处理主要业务。[前文]({{ site.baseurl }}{% post_url 2019-01-28-集成python的Excel插件模板PyAddin——使用说明 %})介绍了`PyAddin`的基本用法，本文简要说明设计思路及其实现。

## 基本原理

VBA通过命令行执行python脚本处理主要任务，然后获取python返回值用于显示。

```
+-------+   python main.py arg1 arg2 ...  +----------+
|  VBA  +-------------------------------->+  python  |
+---^---+                                 +-----+----+
    |           +----------------+              |
    |           |   output.log   |              |
    +-----------+   errors.log   <--------------+
                +----------------+
```


## RunPython()

`RunPython()`是自定义的VBA函数，使用`CreateObject("WScript.Shell").run()`调用指定的python脚本。相比`exec()`的优势是不显示命令行窗口，不足之处是无法直接获取python脚本的执行结果，所以考虑间接地从中间文件读取。其基本代码如下，其中：

- `method_name`指定了需要调用的python脚本，基本规则为`package.module.method`，例如`scripts.test.test_fun`指的是插件主目录下`scripts/test.py`中定义的`test_fun()`方法

- `args`是VBA数组，将其每个元素最为参数传递给被调用的python脚本

- `res`是python脚本的返回信息，如果`RunPython`为True，则为返回值；否则为错误信息

```vb
Function RunPython(method_name As String, args, ByRef res As String) As Boolean
    '''
    ' run python script
    ' :param method_name: a string refer to the called python method -> package.module.method
    ' :param args: array for python arguments
    ' :param res: python return string
    ' :returns: True if everything is OK else False
    '
    '''
    Dim oShell As Object, cmd As String, str_args As String
    Dim log_output As String, log_errors As String, errs As String

    ' TEMP_PATH = addin_path/temp/    
    log_output = TEMP_PATH & "output.log"
    log_errors = TEMP_PATH & "errors.log"
    
    ' join command
    python = """" & ThisWorkbook.Path & "\python\python"" "
    main = """" & ThisWorkbook.Path & "\main.py"" "
    For i = LBound(args) To UBound(args)
        str_args = str_args & " """ & args(i) & """"
    Next
    cmd = python & main & method_name & str_args
    
    ' execute command
    Set oShell = CreateObject("WScript.Shell")
    oShell.Run cmd, 0, 1
    
    ' results
    errs = ReadTextFile(log_errors) ' user defined function
    
    If errs = "" Then
        RunPython = True
        res = ReadTextFile(log_output)
    Else:
        RunPython = False
        res = errs
    End If
    
    Set oShell = Nothing ' clean object
    
    ' remove log file
    If Dir(log_errors, 16) <> Empty Then
        Kill log_output
        Kill log_errors
    End If
    
End Function
```

## main.py

`main.py`是`RunPython`直接调用的函数，它根据传入的方法名称参数`method_name`调用相应的函数。

- `__import__()`根据字符串路径导入模块，注意设置`fromlist=True`以导入多层次的模块，例如`package.module`

- `hasattr()`和`getattr()`判断模块中是否存在指定的方法，存在则调用该方法

- `Logger()`类分别重定向`sys.stdout`和`sys.stderr`到文件`output.log`和`errors.log`，目的是便于`RunPython`函数读取返回值


```python
import sys
import os

main_path = os.path.dirname(os.path.abspath(__file__)) 
sys.path.append(main_path)

from scripts.utility import Logger

# redirect output/error to files
sys.stdout = Logger(os.path.join(main_path, 'temp', "output.log"), sys.stdout)
sys.stderr = Logger(os.path.join(main_path, 'temp', "errors.log"), sys.stderr)

if __name__ == '__main__':

    # python main.py package.module.method *args
    key, *args = sys.argv[1:]

    m = key.split('.')
    module_file = os.path.join(main_path, '{0}.py'.format('/'.join(m[:-1])))
    if os.path.exists(module_file):

        # import module dynamically
        module = __import__('.'.join(m[:-1]), fromlist=True)

        # import method
        if hasattr(module, m[-1]):
            f = getattr(module, m[-1])
            if hasattr(f, 'UDF'):
                f(*args)
            else:
                sys.stderr.write('Please decorate your callback function with @udf')
        else:
            sys.stderr.write('Error Python method "{0}"'.format(m[-1]))
    else:
        sys.stderr.write('Error Python module "{0}"'.format('.'.join(m[:-1])))
```

## @udf装饰器

`main.py`中`hasattr(f, 'UDF')`对被调用的python方法是否具备自定义的`UDF`属性作了检测，目的是要求所有合法的自定义python函数必须经过`@udf`装饰器的装饰。该装饰器将被调用函数的正常返回重定向到`output.log`，将错误信息重定向到`errors.log`。否则，VBA主调函数将无法获取python脚本的返回值。

```python
def udf(fun):
    '''decorator for user defined function called by VBA'''
    
    def wrapper(*args, **kwargs):
        res = None
        try:
            res = fun(*args, **kwargs)
        except Exception as e:
            sys.stderr.write(str(e))
        else:
            if res: sys.stdout.write(str(res))
        return res

    # set a tag that fun is decorated
    setattr(wrapper, 'UDF', True)

    return wrapper
```