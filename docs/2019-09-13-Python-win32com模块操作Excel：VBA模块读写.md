---
categories: [process automation, python/vba/c++]
tags: [python, VBA]
---

# Python win32com模块操作Excel：VBA模块读写


---

Python有很多强大的第三方库可以读写Excel，例如`xlrd`、`xlwt`、`xlutils`、`openpyxl`、`xlwings`等，它们主要在读写方面具备优势，但论起对Excel操作的全面性和基础性，则首推`win32com`，它是`pywin32`库 [^1] 的一部分。本文以代码片段方式记录使用`win32com`读写、运行VBA宏代码。

正如直接在Excel VBA工程中操作一样，`win32com`可以导出或者导入工作簿中的VBA模块，也可以运行其中的宏。同理，这些操作也受到Excel宏安全性设置的影响，因此这一部分从导入/导出宏和运行宏两部分介绍基本代码及相应的宏设置。

## 导入/导出模块

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
        for line in f:
            if line.startswith('Attribute VB_Name'):
                module_name = line.split('"')[-2]
                break
        else:
            raise Exception('Error: Invalid module file.')
    # check modules and remove original one
    for comp in wb.VBProject.VBComponents:
        if comp.Name == module_name:
            print(f'[info] module {module_name} already exists, remove it now.')
            wb.VBProject.VBComponents.Remove(comp)
            break
    # import 
    wb.VBProject.VBComponents.Import(module_file)

    return module_name
```

## 读取/更新模块

上面是以文件的形式导入/导出模块代码，当然还可以以文本形式读取/更新模块代码。

```python
def get_module(wb, name):
    ''' Get the module content from the workbook. '''
    cm = wb.VBProject.VBComponents(name).CodeModule
    num = cm.CountOfLines
    return cm.Lines(1, num) if num else ''


def get_modules(wb):
    ''' Get all modules contents from the workbook and return a dictionary. '''
    for module in wb.VBProject.VBComponents:
        yield module.Name, module.Type, get_module(module.Name)


def set_module(wb, name, code):
    ''' update code of specified module '''
    comp = wb.VBProject.VBComponents(name)
    assert comp, f'Module {name} does not exist in the workbook.'

    cm = comp.CodeModule
    num = cm.CountOfLines
    if num > 0:
        cm.DeleteLines(1, num)

    cm.AddFromString(code)

    # save
    wb.Save()
```

## 运行宏

VBA中`Application.Run()`可以运行宏，我们同样可以在`win32com`模块使用相应的函数。

```python
def run_macro(wb, macro_name):
    '''run macro embedded in current toll
       :param macro_name: macro name, e.g. workbook_name!mudule_name.sub_name

       if errors exist in the macro, this function will be blocked. so ensure the macro works
       well and insert the following macro at the beginning for safe:

       On Error Resume Next

    '''
    try:
        wb.Application.Run(macro_name)        
    except Exception as e:
        print(e, flush=True)
        return False
    else:
        return True
```


## 注意事项

### 操作宏的Excel设置

成功使用`win32com`操作宏的前提是 **允许访问VBA工程对象模型**：`File` -> `Option` -> `Trust Center Setting...` -> `Macro Settings`。否则，提示无权获取VBA工程的模块。

```
Programmatic access to Visual Basic Project is not trusted.
```

除了手动设置上述选项外，还可以程序的方式动态修改：这个选项的开关是注册表项目下`AccessVBOM`字段控制的，0表示禁用，1表示启用。因此安全的做法是在访问VBA模块前修改该设置，这可以通过Python操作注册表来实现。以Excel 2010为例：

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


### 运行宏的Excel设置


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


### 更新宏的问题

上面更新模块代码的函数`set_module(wb, name, code)`，有时会出现莫名其妙的问题：在`name`模块的末尾多出了一对括号`()`。也就是说准备设置`code`，结果却是`code`+`()`。

根据`stackoverflow`上的一个提问 [^2]，原因在于：**`win32com`处理VBA时无法完全正确地识别VBA的续行符`_`**。

例如，当`code`中包含下面片段时：

```vb
Private Declare PtrSafe Function foo Lib "bar.dll" _
    Alias "foo_bar" ( _
    ByVal x As Long, _
    ByVal y As Long) As Long
```

括号中的两个续行符`_`可以被正确识别，但第一行孤立的`_`则出现了问题，于是VBA的自动完成机制导致了最后的一对`()`。

所以尽量避免出现上述写法，或者强制将末尾的`_`删除并合并相应的两行。


[^1]: [Python for Windows (pywin32) Extensions](https://github.com/mhammond/pywin32)
[^2]: [Problem with AddFromString function of CodeModule in VBA](https://stackoverflow.com/questions/58019991/problem-with-addfromstring-function-of-codemodule-in-vba)