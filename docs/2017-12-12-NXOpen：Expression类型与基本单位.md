---
layout: post
author: Train
description: NX表达式概要及NXOpen函数
keywords: NX, NXOpen, Expression
tags: [NX, NXOpen]
---

# NXOpen：Expression类型与基本单位

---

本文参考[NXOpen::Expression Class Reference](https://docs.plm.automation.siemens.com/data_services/resources/nx/12/nx_api/custom/en_US/open_c++_ref/a03679.html)，记录NX表达式知识及相关的NX Open C++函数。

## 表达式类型及获取值的函数

常用表达式类型及获取相应表达式的值的成员函数如下表所示：

类型 | 方法
--- | --- 
Number | Value()
String | StringValue()
Integer | IntegerValue()
Boolean | BooleanValue()
Point | PointValue()
Vector | VectorValue()

- Expression类的`Type()`成员函数可以返回NXString类型的表达式类型名称
- `RightSideHand()`方法可以返回NXString类型的表达式右侧的值

## Number类型与Units

以上类型仅Number类型表达式带有Units（Number类型不为Constant即表示带有单位）。相应地，`Value()`方法返回的是基于基本单位（base part unit）的值。于是，直接使用`Value()`方法获取的表达式值可能和预期不一致。

以Number表达式Unit为Pressure为例，选择单位"PresureNewtonPerSquareMillimeter"，即`N/mm^2`，亦即`MPa`，创建表达式`f=2 MPa`，使用`Value()`函数获取的结果却是`2000.0`。这是因为基本单位是"PressurePerUnitLength"，即`m*N/mm^3`，于是：

    value = 2 m*N/mm^3 = 2000.0 MPa

同理，对于Number类型表达式特有的`SetValue(double)`方法，也是以基本单位为参考的数值。

为了避免以上问题，可以使用函数：

    GetValueUsingUnits(Expression::UnitOption)

即根据指定单位返回表达式的值，其中

    Enum UnitOption {
        UnitOptionBase, UnitOptionExpression
    }