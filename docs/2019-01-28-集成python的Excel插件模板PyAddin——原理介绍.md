---
layout: post
author: Train
description: 使用python开发Excel插件
keywords: Python, vba
tags: [VBA, python]
---

# 集成python的Excel插件模板PyAddin——原理介绍

---

`PyAddin`是一个Excel插件模板，方便在VBA中调用Python脚本处理主要业务。[前文](2019-01-28-集成python的Excel插件模板PyAddin——使用说明.md)介绍了`PyAddin`的基本用法，本文简要说明设计思路及其实现。

## 基本原理

### 1. 自定义插件Ribbon界面

Excel2007及更高版本的各类Excel文件，包括插件`*.xlam`实际上都是`XML`格式组织的压缩文件，其中`CustomUI.xml`定义了插件Ribbon区域的界面形式，因此可以程序化生成此文件来实现插件UI的自动化创建和更新。`CustomUI.xml`文件结构及利用该结构创建插件的方法可以参考：

> [Customizing the 2007 Office Fluent Ribbon for Developers](https://docs.microsoft.com/en-us/previous-versions/office/developer/office-2007/aa338202(v%3doffice.12))
>
> [Microsoft Excel 2010自定义功能区(二)](2017-07-24-Microsoft-Excel-2010自定义功能区(二).md)

### 2. Python自定义VBA模块

创建Excel插件需要的另一个自动化操作是生成默认的菜单按钮回调函数，也就是Python操作Excel VBA的问题。这里采用Python第三方库`pywin32`来实现，具体的操作函数与VBA类似。参考链接：

> [VBProject：代码操作代码之常用语句](https://blog.csdn.net/fenghome/article/details/10373393)


### 3. VBA与Python交互

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

`RunPython()`是自定义的VBA函数，使用`CreateObject("WScript.Shell").run()`调用指定的python脚本。相比`exec()`的优势是不显示命令行窗口，不足之处是无法直接获取python脚本的执行结果，所以考虑间接地从中间文件读取。


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

- `method_name`指定了需要调用的python脚本，基本规则为`package.module.method`，例如`scripts.test.test_fun`指的是插件主目录下`scripts/test.py`中定义的`test_fun()`方法

- `args`是VBA数组，将其每个元素最为参数传递给被调用的python脚本

- `res`是python脚本的返回信息，如果`RunPython`为True，则为返回值；否则为错误信息



## main.py

`main.py`是`RunPython`直接调用的函数，它根据传入的方法名称参数`method_name`调用相应的用户自定义python脚本。为了使VBA主调函数能够获取到python脚本的返回值，需要将标准输出和标准错误重定向到文件。`main.py`的主函数如下： 

- 首先重定向标准输出/错误：正常返回重定向到`output.log`，错误信息重定向到`errors.log`
- 然后动态调用指定的python脚本，并传入参数

```python
if __name__ == '__main__':

	# redirect output/error to output.log/errors.log
	sys.stdout = Logger(os.path.join(main_path, 'temp', "output.log"), sys.stdout)
	sys.stderr = Logger(os.path.join(main_path, 'temp', "errors.log"), sys.stderr)

	# python main.py package.module.method *args
	run_python_method(sys.argv[1], *sys.argv[2:])
```

### 重定向标准输出/错误

```python
class Logger(object):
    '''redirect standard output/error to files, which are bridges for
    communication between python and VBA
    '''
     
    def __init__(self, log_file="out.log", terminal=sys.stdout):
        self.terminal = terminal
        self.log = open(log_file, "w")
 
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
 
    def flush(self):
        pass
```

将此类实例赋值给`sys.stdout`和`sys.stderr`，即可在标准输出/错误的基础上，同时重定向结果到指定文件。前者方便调试时查看信息，后者便于VBA主调函数获取返回值。

### 重定向函数返回值

定义一个装饰器函数`redirect()`对函数的返回值（正常返回/异常捕获）进行重定向输出。

```python
def redirect(fun):
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

    return wrapper
```

### 动态调用指定函数

```python
@redirect
def run_python_method(key, *args):
	'''call method specified by key with arguments: args
	'''
	*modules_name, method_name = key.split('.')
	module_file = os.path.join(main_path, '{0}.py'.format('/'.join(modules_name)))

	# import module dynamically if exists
	module_path = '.'.join(modules_name)
	assert os.path.exists(module_file), 'Error Python module "{0}"'.format(module_path)
	module = __import__(module_path, fromlist=True)

	# import method if exists
	assert hasattr(module, method_name), 'Error Python method "{0}"'.format(method_name)
	fun = getattr(module, method_name)

	return fun(*args)
```

- `__import__()`根据字符串路径导入模块，注意设置`fromlist=True`以导入多层次的模块，例如`package.module`

- `hasattr()`和`getattr()`判断模块中是否存在指定的方法，存在则调用该方法


