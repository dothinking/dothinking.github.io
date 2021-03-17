---
layout: post
author: Train
description: NX Groups与Regions介绍与区别
keywords: NX, NXOpen, Groups, Regions
tags: [NX, NXOpen]
---

# NXOpen CAE开发总结系列：Groups与Regions

---

NX FEM与Simulation部分经常会遇到两个概念`Groups`与`Regions`，它们都可以用来存储一些可重用的对象，便于统一管理。那么，二者有何区别？本文以NX帮助文档为基础，介绍Groups与Regions的概念及其差异，以作学习记录和备忘。

## 定义

`Groups`是几何（点/线/面等）或有限元对象（网格/节点/单元等）的集合。人为选取某些对象并将其定义为一个Group，以便于通过这个Group来统一操作所有被包含的对象，例如导出、施加边界条件、控制显示/隐藏。这类似于MSC.Marc中的`Set`，Hypermesh中的`Component`的概念。

> Groups are collections of FE and geometric entities. You can use groups to organize a large model into a small number of easily-managed containers.

`Regions`是Simulation环境下以边界条件施加为目的的多边形几何或CAE对象的集合。

>  A region is a collection of homogenous entities, such as polygon faces. You can then use a region to define the source faces or target faces in boundary condition definitions.

## 存储对象类型

Groups和Regions中存储对象的类型包括：

Group | Region
---|---
Node, Element | Node, Element
Element edge/face | Element edge/face
Polygon edges/faces/bodies | Polygon edges/faces
meshes, Mesh points | -
Curves, Points | -
Coordinate systems | -

## 使用环境

我们可以在FEM或者Simulation环境创建Groups，它们都显示于Simulation Navigator导航树上。但是注意，**无法在Simulation环境修改FEM环境创建的Groups，反之同理**。

- 当前显示部件为Simulation Part时，FEM环境创建的Groups将附加FEM文件名后显示于Simulation Navigator（例如名称`body`=>`body(CD1-fem_1.prt)`）。因此，FEM Groups可用于Simulation环境边界条件的定义。

- 当前显示部件为FEM Part时，Simulation环境创建的Groups不会显示于Simulation Navigator。

- 当前工作部件为FEM Part时，Simulation环境创建的Groups则会显示于Simulation Navigator。因此，Simulation Groups可用于FEM环境下网格划分区域的设置。

## 导出求解文件

存储在`Groups`与`Regions`中的元素都可以导出为有限元求解文件，以下是它们的一些异同点：

- 使用NX内置的`File`->`Export`->`Export Simulation`将当前模型导出为有限元输入文件`*.inp`时，Groups中存储的Node和Element类型对象默认将被自动导出为以组名命名的集合；而Regions中的对象则不会被导出。但是，如果在导出对话框中关闭导出Group的选项，则不再导出Group。

- Groups中的Node和Element类型对象将分别导出为节点和单元，其他几何对象如Polygon Face、Polygon Edge则导出为空；Regions中所有类型对象，即便是Elements，都将被导出为离散后后的节点集合。

- 修改几何模型将导致网格的更新，此时Groups和Regions中存储的Node及Element类型对象都将失效，表现为集合为空；而Polygon Face、Polygon Edge类型依旧可以保持正确的对应关系，所以可以导出为更新后的节点集合。

## 小结

- Groups是FEM或Simulation环境下一系列可重用对象的集合，方便后续作为整体进行统一管理。Regions是以CAE中施加边界条件为目的而组织的CAE元素的集合。概括而言，Groups可存储的类型更多，Regions主要面向CAE边界条件的施加。

- Groups中的Node、Element对象将自动导出为相应类型集合，Regions中所有类型可以手动导出为节点的集合。

- 模型更新后，无论Groups还是Regions中的Node及Element类新对象都将失效，而Polygon类型对象将自动更新。

## 参考资料

- [Simcenter 3D (CAE)Simcenter Pre/PostGroups](https://docs.plm.automation.siemens.com/tdoc/nx/12/nx_help#uid:xid1128419:index_advanced:xid1159750:id625201)  

- [Working with reusable regions](https://docs.plm.automation.siemens.com/tdoc/nx/12/nx_help/#uid:id911964) 

- [Region dialog box (Samcef)](https://docs.plm.automation.siemens.com/tdoc/nx/12/nx_help/#uid:xid919887)  