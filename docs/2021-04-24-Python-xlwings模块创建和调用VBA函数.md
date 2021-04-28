---
categories: [process automation]
tags: [python]
---

#  Python xlwings模块创建和调用VBA函数


---

`xlwings`是`win32com`的高级封装，其中`xlwings.App.macro(name)`方法可以直接调用VBA模块中定义好的函数。结合[前文](2019-09-13-Python-win32com模块操作Excel：VBA模块读写.md)`win32com`操作VBA模块的方法，这就产生了一种新的使用方式：**直接用Python注入VBA代码并获取该函数句柄，然后在Python中调用，最后实际以VBA方式执行**。

我们当初选择xlwings是为了简化VBA代码，那为何还要回过头来写VBA呢？xlwings的简化是以性能损耗为代价的，因此对于需要提高性能的场景，可以考虑本文方法。接下来，我们通过一个假设的场景来演示整个过程。

## 需求

假设需要填写`target.xlsm`每一个工作表中红色背景的单元格，它的值来源于`source.xlsx`相同位置的单元格。

考虑单个工作表，我们可以借助xlwings的API遍历`target.xlsm`中已使用的单元格并判断背景色，满足要求则提取其地址；然后提取`source.xlsx`相应位置单元格的值，并赋值到`target.xlsm`的单元格。整个过程不复杂，但是随着数据量增大，运行时间逐渐难以接受。


## 自定义VBA函数

检查发现主要时间花费在目标单元格的遍历识别上，因此考虑使用VBA原生方法：

    Function GetRange(sheetName)
        Dim rng As Range, res As Range
        Set res = Nothing
        For Each rng In ThisWorkbook.Worksheets(sheetName).UsedRange
            If rng.Interior.Color = RGB(255, 0, 0) Then
                If res Is Nothing Then Set res = rng Else: Set res = Union(res, rng)
            End If
        Next    
        Set GetRange = res
    End Function


## 注入和引用VBA函数

然后利用xlwings在`target.xlsm`创建VBA模块并写入上述函数：

    import xlwings as xw

    # Excel application
    app = xw.App(add_book=False, visible=False)
    app.screen_updating = False
    app.display_alerts = False
    app.api.AutomationSecurity = 1

    # open target.xlsm
    com_target = app.books.api.Open('path/to/target.xlsm', UpdateLinks=False) # win32com object
    wb_target = app.books[com_target.Name] # xlwings object

    # add module and inject codes
    code = '''...GetRange code...'''
    insert_module('any_module_name')
    update_module('any_module_name', code)

    # save
    wb_target.save()

注意`insert_module`和`update_module`分别是创建和更新模块的自定义函数，参考本文开头提及的文章。

接下来，利用`xlwings.Book.macro`获取VBA中定义的函数`GetRange(sheetName, sourceWbName)`：

    fun_get_range = wb_target.macro('GetRange')


## 调用VBA函数

`fun_get_range`作为函数句柄，同`GetRange`的原始定义一样，也带参数`sheetName`，应用举例：

    sheet_names = [sheet.name for sheet in wb_target.sheets]
    for sheet_name in sheet_names:
        # source/target sheets
        target_sheet = wb_target.sheets(sheet_name)
        source_sheet = wb_source.sheets(sheet_name)

        # satisfied ranges in current sheet
        input_ranges = fun_get_range(sheet_name)

        # process with input_ranges
        # ...


!!! warning "注意"
    `fun_get_range()`获取VBA的执行结果，并未经过`xlwings`的包装，仍旧是`win32com`类型的对象。主要区别在于API的首字母，`win32com`通常是首字母大写，而`xlwings`倾向于全部小写。


最后，我们可以遍历`input_ranges`，实现从`source.xlsx`向`target.xlsm`赋值。还有一个提速的小技巧：逐个赋值当然不如连续区域的一次性赋值来的快：

    for area in input_ranges.Areas:
        # fill all cells in same area, here v is a list of list by setting nidm=2
        address = area.Address    
        v = source_sheet.range(address).options(ndim=2).value
        target_sheet.range(address).value = v
