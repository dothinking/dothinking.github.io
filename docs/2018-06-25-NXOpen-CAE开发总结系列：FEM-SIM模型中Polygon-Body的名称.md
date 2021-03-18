---
keywords: NX, FEM, Simulation
tags: [NX,NXOpen]
---

# NXOpen CAE开发总结系列：FEM SIM模型中Polygon Body的名称

2018-06-25

---

我们已经知道`Idealized Part`、`FEM Part`、`SIM Part`中的几何元素具有一定的关联，例如前者的Body对象对应了后两者的Polygon Body，那么它们的名称即Name属性在关联关系上有何注意事项呢？

- `Idealized Part`中Body的Name属性决定了其在`FEM Part`中对应的Polygon body的Name属性。

- Polygon body的Name属性有两种等效的维护途径：

    1. 选中Polygon body->右键->Attribute。

    2. 仿真导航器->FEM->Polygon Geometry->右键->Rename。 
    
        !!! warning "注意操作上的一个细节："
            假设方法1中`Name=TEST`，则此处显示的是`TEST(id)`，其中`id`为该对象的编号。那么，直接rename时的默认名称是`TEST(id)`即等效为`Name=TEST(id)`，这就产生了与预期不相符的结果。

- 重命名`FEM Part`中的Polygon body后仍然可以改回原来的链接自`Idealized Part`中Body对象的名称：仿真导航器->FEM->Polygon Geometry->右键->Synchrorize to CAD name。

    !!! warning "注意"
        此时只是修改了polygon body的显示名称，Attribute中的Name依旧是修改前的值。为了保证Name属性的统一，应该在Synchrorize to CAD name后马上rename为该默认的名称。

- 作为Occurrence，`SIM Part`中对应的Polygon body默认继承了`FEM Part`中的原始名称，并且`FEM Part`中的重命名也就同步更新`SIM Part`的Polygon body。

    但是，**一旦为`SIM Part`的Polygon body显式地设置了名称（并且此名称不同于继承的默认名称），则打破了自动继承关系，其名称不再随着`FEM Part`中polygon body名称的改变而改变**。
