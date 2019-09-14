---
layout: post
author: Train
description: Python操作Excel
keywords: python, win32com
tags: [python, VBA]
---

Python有很多强大的第三方库可以读写Excel，例如`xlrd`、`xlwt`、`xlutils`、`openpyxl`、`xlwings`等，它们主要在读写方面具备优势，但论起对Excel操作的全面性和基础性，则首推`win32com`，它是`pywin32`库[[^1]]的一部分。本文记录使用`win32com`操作Excel的几个案例，例如一般的读写操作、导入/导出/运行VBA宏、引用管理等。

## 安装

```
pip install pywin32

# 如果需要用到系统功能例如注册COM对象、Windows服务，则需要继续执行如下安装
python Scripts/pywin32_postinstall.py -install
```

## 基本操作

由于`win32com`是对基本COM API的封装，所以基本功能的使用和VBA极为类似，因此本文不会在此方面花费篇幅，仅以如下例子作参考：

```python
import win32com.client

# 获取Excel Application
# app = win32com.client.gencache.EnsureDispatch("Excel.Application")
app = win32com.client.Dispatch("Excel.Application")
app.Visible = False
app.DisplayAlerts = False
app.ScreenUpdating = False

# 打开工作簿
wb = app.Workbooks.open("path/to/workbook")

# 获取工作簿后则可类似VBA操作，例如获取当前工作表，进而获取Range等
# Range具有Value, Address, Formula属性
wb.ActiveSheet.Range("A1").Value = "Hello World"

```

其中使用`Dispatch()`和`EnsureDispatch()`获取`COM`对象的差别参考[[^2]]。

我们更关心的是如何获取API，对于简单的应用，可以参考VBA代码提示或录制的宏进行转换，但是不能保证其正确性。考虑到`win32com`是对Windows COM组件API的封装，我们可以直接参考原始API文档。如果安装了Visual Studio，可以从如下目录找到`oleview.exe`[[^3]]：

```
C:\Program Files (x86)\Windows Kits\8.1\bin\x64\oleview.exe
```

注意**以管理员方式运行该程序**，否则无法打开后续的文档。然后从左侧面板的`Type Libraries`节点查找需要的内容，例如对于Excel 2010，我们浏览找到`Microsoft Excel 14.0 Object Library (Ver 1.7)`。双击打开后即可看到详细的API文档，包括类及其属性和方法、常量等。


## 开启/关闭工作表保护

`Protect()`和`Unprotect()`开启/关闭工作表保护，适用于对有保护的工作表的自动化处理。下面示例代码检测工作表保护状态，如果被保护则取消保护以便修改操作，最后还原之前的保护状态：

```python
# check protection status
status = sheet.ProtectContents
if status:
    sheet.Unprotect()

# DO SOMETHING

# reset protection status
if status:
    sheet.Protect()
```

## 开启/关闭自动计算 [[^4]-[^5]]

Excel默认开启自动计算，那么当工作表内单元格公式非常多时，每录入一个数据都将触发相关单元格的更新计算，影响操作效率。因此此种情况下，一般先设置为手动更新，待输入完成后设置自动更新。以下为示例代码：

```python
# sample Excel and workbook
app = win32com.client.Dispatch("Excel.Application")
wb = app.Workbooks.open("path/to/workbook")

# turn off automatic calculation to improve performance
# otherwise, the entire worksheet will re-calculate every time a new input is entered
app.Calculation = -4135 # xlCalculationManual

# DO SOMETHING, e.g. ENTER DATA

# turn on automatic calculation: xlCalculationAutomatic
# but sometimes it's not able to re-calculate, so we should trigger it explicitly:
# https://docs.microsoft.com/en-us/office/client-developer/excel/excel-recalculation
# from the link, a simple way is adding an empty row, e.g. Row No.1000000,
# then the active worksheet is re-calculated
# 
# here we force to re-calculate the entire workbook
# 
app.Calculation = -4105
wb.Application.CalculateFullRebuild()
```

## VBA宏操作

正如直接在Excel VBA工程中操作一样，`win32com`可以导出或者导入工作簿中的VBA模块，也可以运行其中的宏。同理，这些操作也受到Excel宏安全性设置的影响，因此这一部分从导入/导出宏和运行宏两部分介绍几本代码及相应的宏设置。

### 导入/导出宏

`workbook.VBProject.VBComponents`获取所有VBA模块，因此可以进行导出/读取内容操作：

```python
def export_module(wb, module_name, saved_file):
    '''export vba module to file'''
    for comp in wb.VBProject.VBComponents:
        if comp.Name == module_name:
            comp.Export(saved_file)
            return True
    else:
        return False

def read_module(wb, module_name):
    '''get source codes from module with name module_name'''
    for comp in wb.VBProject.VBComponents:
        if comp.Name == module_name:
            num = comp.CodeModule.CountOfLines
            src = comp.CodeModule.Lines(1,num)
            break
    else:
        src = None
    return src
```

上面`Export()`方法导出的宏文件是以`Attribute VB_Name = "xxxx"`开头的，然后才是代码正文。相应地，我们可以先判断第一行得到宏的名称，然后用`Import()`方法进行导入，并且注意不可重复导入已存在的模块，可以根据需要选择保留或者替换原模块。

```python
def import_module(wb, module_file):
    '''
        import vba module from *.bas.
        module name is declared in the first line of module_file:
        Attribute VB_Name = "xxxx"
    '''
    # check module name
    with open(module_file, 'r') as f:
        header = f.readline()
    if header.startswith('Attribute VB_Name'):
        module_name = header.split('"')[-2]
    else:
        raise Exception('The first line of a valid module file should be: Attribute VB_Name = "xxxx"')
    # check modules and remove original one
    for comp in wb.VBProject.VBComponents:
        if comp.Name == module_name:
            wb.VBProject.VBComponents.Remove(comp)
            break
    # import 
    wb.VBProject.VBComponents.Import(module_file)
```

上述代码可以正确运行的前提是**允许访问VBA工程对象模型**的选项是打开的——`File` -> `Option` -> `Trust Center Setting...` -> `Macro Settings`。否则，提示无权获取VBA工程的模块。

```
Programmatic access to Visual Basic Project is not trusted.
```

这个选项的开关是注册表项目下`AccessVBOM`字段控制的，0表示禁用，1表示启用。因此安全的做法是在访问VBA模块前修改该设置，这可以通过Python操作注册表来实现。以Excel 2010为例：

```python
import win32api
import win32con

def access_VBA_object_model(value):
    '''programmatically enable access to the VBA object module
       :param value: 0->disabled, 1->enabled
    '''
    # open registry on Excel2010
    key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,
                        'Software\\Microsoft\\Office\\14.0\\Excel\\Security', 0, win32con.KEY_ALL_ACCESS)
    # store original value
    val, _ = win32api.RegQueryValueEx(key,'AccessVBOM') # (value, type)

    # set value:
    # the property name "AccessVBOM" could be check from Registry
    win32api.RegSetValueEx(key, "AccessVBOM", 0, win32con.REG_DWORD, value)

    # close
    win32api.RegCloseKey(key)

    return val
```

上述代码记录了修改前的值，以便处理完后恢复原来的设置。


### 运行宏

VBA中`Application.Run()`可以运行宏，我们同样可以在`win32com`模块使用相应的函数。

```python
app = win32com.client.Dispatch("Excel.Application")
app.Application.Run(macro_name)
```

运行宏同样存在安全策略的设置问题。根据系统设置策略，不在信任区域的宏代码可能是默认被禁用的，那么执行上述代码将提示不存在该宏。Excel软件中对应这个设置的操作是：`File` -> `Option` -> `Trust Center Setting...` -> `ActiveX Settings`，其中有不同的选项例如默认禁用、默认禁用但打开工作簿时给予提醒、全部启用等。

程序中则由`Application`的`AutomationSecurity`属性控制：2表示禁用所有宏, 1表示启用所有宏。如果来源确实可靠的话，我们可以在执行宏前启用所有宏，最后修改回之前的设置即可。

```python
app = win32com.client.Dispatch("Excel.Application")
# save original value
origin_val = app.Application.AutomationSecurity
# enable all
app.Application.AutomationSecurity = 1
# run macro here
# ...
# reset
app.Application.AutomationSecurity = origin_val
```

## 引用管理

VBA代码可能跨工作簿引用函数，例如COM组件中的类和方法，但前期可能没有正确加载该引用。手工加载引用的流程为：`Developer` -> `Visual basic` -> `Tools` -> `References...`，而`workbook.VBProject.References`则从程序设置的角度管理当前VBA工程已经添加的引用。

一个引用通常包含名称、路径、版本号等信息，我们首先可以遍历显示所有已加载引用的信息：

```python
for ref in wb.VBProject.References:
    print(ref.Name, ref.FullPath, ref.GUID, ref.Major, ref.Minor, ref.Description)
```

`AddFromFile()`和`AddFromGuid()`方法可以通过文件路径和`GUID`的方式添加引用，其中`GUID`由创建COM组件时生成并已注册到系统。注意不能重复添加，即如果丢失则自动添加，否则不处理。

```python
guid, major_version, minor_version = "{662901FC-6951-4854-9EB2-D9A2570F2B2E}", 1, 0
loaded = False
for ref in wb.VBProject.References:
    if ref.GUID == guid:
        if ref.IsBroken: # loaded but broken
            wb.VBProject.References.Remove(ref)
        else:
            loaded = True

if not loaded:
    wb.VBProject.References.AddFromGuid(guid, major_version, minor_version)
```

显然，这部分代码也需要设置**允许访问VBA工程对象模型**，因为用到了`wb.VBProject`。

---

[^1]: [1] [Python for Windows (pywin32) Extensions](https://github.com/mhammond/pywin32)
[^2]: [2] [win32.Dispatch vs win32.gencache in Python. What are the pros and cons?](https://stackoverflow.com/questions/50127959/win32-dispatch-vs-win32-gencache-in-python-what-are-the-pros-and-cons)
[^3]: [3] [OLE-COM Object Viewer](https://docs.microsoft.com/zh-cn/windows/desktop/com/ole-com-object-viewer)
[^4]: [4] [Excel Recalculation](https://docs.microsoft.com/en-us/office/client-developer/excel/excel-recalculation)
[^5]: [5] [Getting Excel to refresh data on sheet from within VBA](https://stackoverflow.com/questions/154434/getting-excel-to-refresh-data-on-sheet-from-within-vba)