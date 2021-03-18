---
layout: post
author: Train
description: NX Mesh与ANSYS input文件对应关系
keywords: NX, FEM, Simulation
tags: [NX,NXOpen]
---

# NXOpen CAE开发总结系列：从ANSYS APDL角度看待Mesh

---

在NX中创建Simulation时需要指定求解器类型，本文在指定ANSYS求解器的前提下，分析FEM模块Mesh相关操作与最终导出的ANSYS input文件之间的对应关系。

## APDL单元类型号命令

APDL设置单元类型号命令：

    ET, N, PLANE183 ! 设置第N号单元类型（Element Type）为PLANE183


为指定的Element Type设置关键参数`KEYOPT`：

    KEYOPT, N, 3, 1 ! ET=N的KEYOPT(3)=1，即轴对称类型


## NX Mesh相关操作

- 不同几何体的网格划分结果存储在`Mesh Collector`下。
- 在仿真导航器中选择Mesh节点后，可以在右键菜单中编辑`Mesh associated data`，其中包含`Name`、`Label`，`KEYOPT`等属性。
- File->Export->Simulation，设置导出类型为ANSYS

关系示意图：

    +-------------------------+
    |  Mesh Collector         |
    |     +--+ 2d_mesh(1)     |   mesh associated
    |     +--+ 2d_mesh(2) +------+data
    |              Simulation |      |
    +--------+----------------+      |
            |               +-------v----------+
            |               | Name   : ---     |
            |               | Label  : 2       |
            |               | KEYOPTS: +-+     |
            |               +------------------+
            +---------+-------------+
                    |
                +------v------+
                |ET,2,PLANE183|
                |...          |
                +------+------+
                    |
    +------------------v------------------------+
    |   !MAT ET R XSec Eds EL Nodes             |
    |   ..........                              |
    |   ..........                              |
    |                                 ansys.inp |
    +-------------------------------------------+


## 对应关系

- 每个Mesh（例如`2d_mesh(1)`）对应一个唯一的编号，默认为1,2,3...，对应了导出的inp文件中的`ET`号。
- `mesh associated data`属性等同于ANSYS的`ET`的定义，其中`Label`对应`ET`号。
- 导出inp文件时，综合以上两点分配`ET`号。出现冲突时，以`mesh associated data`的`Label`值为准，默认的冲突值顺延直至消除冲突。
- 最后，`ET`号将添加到属于该Mesh的所有Element上。