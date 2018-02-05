---
layout: post
author: Train
description: NX Groups与Regions介绍与区别
keywords: NX, NXOpen, Groups, Regions
tags: [NX, NXOpen]
---

NX FEM与Simulation部分经常会遇到两个概念`Groups`与`Regions`，它们都可以用来存储一些可重用的对象，便于统一管理。那么，二者有何区别？本文以NX帮助文档为基础，介绍`Groups`与`Regions`的概念及其差异，以作学习记录和备忘。

## Groups
`Groups`是几何（点/线/面等）或有限元对象（网格/节点/单元等）的集合。人为选取某些对象并将其定义为一个`Group`，以便于通过这个`Group`来统一操作所有被包含的对象，例如导出、施加边界条件、控制显示/隐藏。这类似于MSC.Marc中的`Set`，Hypermesh中的`Component`的概念。

> Groups are collections of FE and geometric entities. You can use groups to organize a large model into a small number of easily-managed containers.

`Groups`对象通常可以存储以下类型

- Nodes, elements, meshes
- Element edges, element faces
- Mesh points, points
- Polygon edges, polygon faces, polygon bodies
- Curves
- Coordinate systems

我们可以在`FEM`或者`Simulation`环境创建`Groups`，它们都显示于`Simulation Navigator`导航树上。但是注意，**无法在`Simulation`环境修改`FEM`环境创建的`Groups`，反之同理**。

- 当前显示部件为`Simulation Part`时，`FEM`环境创建的`Groups`将附加`FEM`文件名后显示于`Simulation Navigator`（例如名称`body`=>`body(CD1-fem_1.prt)`）。因此，`FEM Groups`可用于`Simulation`环境边界条件的定义。

- 当前显示部件为`FEM Part`时，`Simulation`环境创建的`Groups`不会显示于`Simulation Navigator`。

- 当前工作部件为`FEM Part`时，`Simulation`环境创建的`Groups`则会显示于`Simulation Navigator`。因此，`Simulation Groups`可用于`FEM`环境下网格划分区域的设置。

## Regions

`Regions`是`Simulation`环境下以边界条件施加为目的的多边形体或CAE对象的集合。

>  A region is a collection of homogenous entities, such as polygon faces. You can then use a region to define the source faces or target faces in boundary condition definitions.

因为需要导出为`CAE`模型，`Regions`是与求解器相关的。总的来说，`Regions`存储对象的类型有：

- Edge
- Surface
- Element Face
- Element Edge
- Node
- Element
- 

## 小结

`Groups`是`FEM`或`Simulation`环境下一系列可重用对象的集合，方便后续作为整体进行统一管理。`Regions`是以CAE中施加边界条件为目的而组织的CAE元素的集合。概括而言，`Groups`通用性更强，`Regions`主要面向CAE边界条件的施加。

## 参考资料

[1] [Simcenter 3D (CAE)Simcenter Pre/PostGroups](https://docs.plm.automation.siemens.com/tdoc/nx/12/nx_help#uid:xid1128419:index_advanced:xid1159750:id625201)  

[2] [Working with reusable regions](https://docs.plm.automation.siemens.com/tdoc/nx/12/nx_help/#uid:id911964) 

[3] [Region dialog box (Samcef)](https://docs.plm.automation.siemens.com/tdoc/nx/12/nx_help/#uid:xid919887)  