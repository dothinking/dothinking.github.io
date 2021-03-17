---
layout: post
author: Train
description: NX Advanced Simulation 文档结构
keywords: NX, FEM, Simulation
tags: [NX,NXOpen]
---

本文从NX Open二次开发的角度，介绍NX有限元分析涉及的文件结构（Part类型）及不同部件间相关几何对象的引用关系。

## 文件/部件类型

NX中根据CAD模型创建有限元分析模型过程中将涉及四种类型的文件：CAD主模型(master part)、理想化几何模型(idealized part)、有限元模型(FEM part)及仿真模型(simulation part)。它们相互关联并各司其职：

- **CAD主模型** 需要分析的几何对象，并不要求具有可编辑权限
- **理想化几何模型** 有限元分析前的几何清理，例如抽中面、分割部件、简化特征等。理想化几何模型关联自主模型，可以响应主模型的更新却不会反向污染主模型。
- **有限元模型** 网格划分、单元设置、材料属性
- **仿真模型** 边界条件设置、求解参数控制及后处理显示

## 文档结构与装配结构

仿真导航器（Simulaton Navigator）和仿真文件视图（SImulation File View）展示了如下的文件结构：

```
+---------------------------------------+
| SIM Part                              |
|    +                                  |
|    +---+ FEM Part                     |
|             +                         |
|             +---+ Idealized Part      |
|                        +              |
|                        +---+ CAD Part |
+---------------------------------------+
```

设置不同部件为工作部件时，装配树（Assembly Navigator）结构如下所示。从中可以看出，这四类文件中，有限元模型是仿真模型的装配组件，CAD模型是理想化几何体的装配组件。

```
+---------------------+  +--------------------+
|CAD Part             |  |Idealized Part      |
|    +                |  |   +                |
|    +--+ Component_1 |  |   +--+ CAD Part    |
|    +--+ Component_2 |  |                    |
|    +--+ ...         |  |                    |
+---------------------+  +--------------------+
+---------------------+  +--------------------+
|FEM Part             |  |SIM Part            |
|                     |  |   +                |
|                     |  |   +--+ FEM Part    |
|                     |  |                    |
+---------------------+  +--------------------+
```

**综合起来看，这是两个不同维度的结构，仿真文档视图组织了四类部件，而针对其中任一类部件，都有与之对应的装配树结构。这样一来，我们将同时涉及部件和同名装配组件两个概念。以当前工作部件为SIM Part为例，我们既可以从仿真导航器获取与之关联的FEM Part，又可以从装配导航器获取与之关联的FEM Component。FEM Part和FEM Component包含从NX操作上来看并无区别的几何对象，然而实际上他们在内存中却是不同的对象。**

## 部件切换与装配组件切换

文档结构树所示关联关系用NXOpen API中相关类的成员函数表示为：

```
                                 IdealizedPart()
                                                +--------+
            FemPart()               +---------->+CAD Part|
+--------+             +--------+   |           +--------+
|SIM Part+------------>+FEM Part+---+
+--------+             +--------+   |           +--------------+
                                    +---------->+Idealized Part|
                                                +--------------+
                                 MasterCadPart()
```

*使用成员函数进行以上切换的前提是相关部件都已经加载到Session中。*

切换到相应部件并设为工作部件后，则可根据上述装配结构图获取相应装配体：

```
       ComponentAssembly()     RootComponent()       GetChildren()
+-----------+     +---------------+     +----------------+     +------------+
| Work Part +-----> Assembly tree +-----> Root Component +-----> Components |
+-----------+     +---------------+     +----------------+     +------------+
```


## 几何对象切换

不同部件间的几何对象具有一一对应关系，例如Idealized Part中的某个Edge对应了FEM Part中的Polygon Edge，进而又对应SIM Part中的Polygon Edge。以上对应关系由NX自动维护，我们可以使用`Open C`函数，根据当前部件中的对象获取处于关系对上的相关对象：

```c
#include <uf_sf.h>
tag_t UF_SF_map_object_to_current_part(tag_t object_tag /*Tag of a object to be mapped*/);
```

我们还可以使用`NXOpen C++`函数实现部件与装配组件中几何对象的切换。某部件中的几何对象`G`将以`Occurrence`的形式`G'`出现在当前工作部件的装配组件中，而这个`G'`也正是`G`对应于当前部件的几何对象。例如，几何对象`MeshPoint`仅能在FEM Part中创建和删除，即真身（Prototype）存在于FEM Part中，同时它也可以出现在SIM Part中（此时可以被选择却不能被修改）。它在SIM Part中的展现形式正是FEM Part中`MeshPoint`在FEM装配组件中的`Occurrence`。下面给出两个具体的例子：

### 新建并存储MeshPoint于SIM Part的Group

基本思路：首先切换到FEM Part创建`MeshPoint`对象，然后根据这个Prototype获取相应的Occurrence，最后存入SIM Part的group中。

得到FEM Part中创建的`MeshPoint`并切换回SIM Part后，我们可以直接使用上述`Open C`函数，此处则演示`NXOpen C++`方法：从装配树获取FEM组件，然后使用其`FindOccurrence()`成员函数获取在SIM Part中的对象。

```
       ComponentAssembly()     RootComponent()

+----------+      +---------------+     +----------------+
| SIM Part +------> Assembly tree +-----> Root Component |
+----------+      +---------------+     +-------+--------+
                                                |
                                                | GetChildren()
+-----------------------+               +-------v--------+
| MeshPoint in SIM Part <---------------+ FEM Component  |
+-----------------------+               +----------------+
                          FindOccurrence()

```


### SIM Part中获取MeshPoint的关联Node

基本思路：FEM Part的`SmartSelectionManager`可以根据`MeshPoint`获取`Node`，需要注意的是此处的`MeshPoint`必须是FEM Part中的`Prototype`。由于Group中存储的`Occurrence`，直接使用`Prototype()`获取即可。

*创建MeshPoint后应更新FEModel，此后才建立MeshPoint与Node的对应关系，CreateRelatedNodeMethod()方法也才生效。但是，当模型十分复杂时，为避免更新FEModel造成的等待时间，亦可遍历节点坐标来获取重合节点。*



















