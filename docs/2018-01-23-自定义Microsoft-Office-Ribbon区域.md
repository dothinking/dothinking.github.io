---
keywords: ribbon, add-in, word, dotm
tags: [VBA]
---

# 自定义Microsoft Office Ribbon区域

2018-01-23

---

[前文](2017-07-24-Microsoft-Excel-2010自定义功能区：修改XML.md)以`Microsoft Excel 2010`为例介绍了制作带有自定义Ribbon菜单的Excel插件的基本流程，实际上此方法通用于`MicroSoft Office`的常用组件：Word，Excel，PPT。这是因为这些Office应用程序文档都是基于`Office Open XML`格式：

> Office Open XML (also informally known as OOXML or Microsoft Open XML (MOX)) is a zipped, XML-based file format developed by Microsoft for representing spreadsheets, charts, presentations and word processing documents.
>
> -- Wikipedia

这种开放的XML文件格式改进了文件和数据管理、数据恢复和可交互操作的能力。它实际上是压缩文件，可以使用解压软件查看文件内部的情况；并且任何支持XML的应用程序都能访问和处理Office文件信息，即只要提供了对XML的支持，即便系统没有安装Office软件、非Office应用程序也可以方便地创建和操纵Office文件。


正是基于这种开放的XML文件格式，才使得[前文](2017-07-24-Microsoft-Excel-2010自定义功能区：修改XML.md)编辑`XML`文件的方法有迹可寻。

---

## `Office Open XML`文档类型

如[Introducing the Office (2007) Open XML File Formats](https://technet.microsoft.com/zh-cn/library/aa338205.aspx/#Developing Solutions Using the Office XML Formats)所述，按Word、Excel、PPT分为三大类：

文档类型 | 扩展名
--- | ---
word文档 | .docx
启用宏的word文档 | .docm
word模板 | .dotx
启用宏的word模板 | .dotm


文档类型 | 扩展名
--- | ---
Excel工作簿 | .xlsx
启用宏的Excel工作簿 | .xlsm
Excel模板 | .xltx
启用宏的Excel模板 | .xltm
启用宏的Excel插件/加载项 | .xlsa

文档类型 | 扩展名
--- | ---
PPT演示文档 | .pptx
启用宏的PPT演示文档 | .pptm
PPT模板 | .potx
启用宏的PPT模板 | .potm
启用宏的PPT插件 | .ppam


## 主要区别

以上类型可以归纳为普通/启用宏文档、普通/启用宏模板、插件，主要区别在于：

* 是否启用宏决定了能否保存和执行自定义VBA代码，通常以`m`结尾的文档为启用宏的类型
* 对文档（普通/宏）的自定义Ribbon操作仅仅影响当前文档
* 对模板或者插件的自定义Ribbon操作将在加载它们后对所有文档生效

因此，我们通常以模板或者插件的形式制作通用的功能，使其可以被所有需要的文档使用。

!!! warning "如何理解“自加载后...”"
    - 插件一旦被启用后，将在每次启动应用程序的时候完成加载
    - 模板分为全局模板（global template）和普通模板，前者伴随应用程序的启动而加载，后者需要手工加载

什么是 **全局模板**（global template）?

以Word为例，位于`C:\Users\username\AppData\Roaming\Microsoft\Word\Startup`下的模板文件（`.dot, .dotx, .dotm`）将在Word启动后完成加载，因此称为全局模板。

可以通过`Developer`->`Add-Ins`查看已加载和启用的模板。当然，通过`Add...`按钮可以临时添加其他任意位置的模板文件。但是它们在下次启动Word后并不会自动完成加载，还需要手工启用。

## 示例

以Word为例演示带有自定义Ribbon菜单的插件的制作：

* 新建Word文档另存为启用宏的模板`.dotm`文件，编写相应VBA代码

* 按照[前文](2017-07-24-Microsoft-Excel-2010自定义功能区：修改XML.md)流程完成自定义Ribbon操作

* 将制作好的`.dotm`模板文件置于`Startup`目录自动加载或者手工按需加载
