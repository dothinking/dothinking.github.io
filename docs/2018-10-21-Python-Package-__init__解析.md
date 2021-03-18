---
categories: [python/vba/c++]
tags: [python]
---

# Python Package __init__解析


---

单个Python文件可以作为一个`Module`被导入重用，多个Module可以组织为`Package`。Package下一般都有一个`__init__.py`文件，而且内容可能啥也没有。本篇即解释此`__init__.py`文件的使用。

## 文件结构

以下文件结构作为本篇试验测试依据：


    +-----------------------------+ +---------------------------------+
    |  + Package                  | |# Package/Sub_Package/module_a.py|
    |  |    |                     | |x = 1                            |
    |  |    + Sub_Package         | +---------------------------------+
    |  |    |      |              |
    |  |    |      + module_a.py  | +---------------------------------+
    |  |    |      + module_b.py  | |# Package/Sub_Package/module_b.py|
    |  |    |      + __init__.py  | |from . import module_a           |
    |  |    |                     | |x = module_a.x + 1               |
    |  |    + module_c.py         | +---------------+-----------------+
    |  |    |                     |
    |  |    + __init__.py         | +---------------------+
    |  + test.py                  | |# Package/module_c.py|
    |                             | |x = 3                |
    +-----------------------------+ +---------------------+


其中，

- `test.py`为测试文件，`Package`为待测试的包
- `Package`包含模块`module_c.py`和子包`Sub_Package`，以及该包的`__init__.py`文件
- `Sub_Package`包含两个模块`module_a.py`和`module_b.py`，以及该包的`__init__.py`文件
- `Sub_Package`中module_a模块被module_b导入使用

以下基于三种不同的导包方式，示例`__init__.py`的作用。

## from Package import module

此为精确导入的形式——明确指定导入模块的名称。这种情况对`__init__.py`没有特殊要求，可以为空甚至不需要该文件。其作用仅仅是表明`Package`文件夹管理的是一个包。

```python
# test.py
from Package import module_c
print(module_c.x) # 3

# 导入子包中的模块
from Package.Sub_Package import module_a
print(module_a.x) # 1
```

## from Package import *

如果依旧保持`__init__.py`为空，则下面代码无法正确导入module_c模块。

```python
# test.py
from Package import *
print(module_c.x) # name 'module_c' is not defined
```

对于这种模糊导入的方式，需要在`__init__.py`中定义变量`__all__`来指定`from Package import *`时所包含的内容。补充如下代码后，即可使用上一段代码正确引入module_c。

```python
# Package/__init__.py
__all__ = ['module_c']
```

`__init__.py`文件会在导入包的时候执行，因此可以在其中进行一些初始化的操作，例如本例中初始化一个变量`x`：

```python
# Package/__init__.py
x = 4
__all__ = ['module_c', 'x']
```

```python
# test.py
from Package import *
print(module_c.x) # 3
print(x) # 4
```
## import Package

实际上，`import Package`不会导入任何模块或者子包，以上例中的`Package/__init__.py`为当前状态，则有：

```python
# test.py
import Package
print(Package.module_c.x) # module 'Package' has no attribute 'module_c'
print(Package.x) # 4
```

由于未导入任何模块，故`Package.module_c`出错；由于导包的时候执行了`__init__.py`，即初始化了变量`x`，故`Package.x`正确。

**解决方法：利用`__init__.py`文件在导入包时被执行的特点，在`__init__.py`中显式导入子模块/子包**。

更新后的文件如下图所示，则上一段代码可以正确执行了。

```python
# Package/__init__.py
from . import module_c # 显式导入子模块
from . import Sub_Package # 显式导入子包
x = 4
__all__ = ['module_c', 'x']
```

以上代码块中`from . import Sub_Package`导入子包，使得可以识别`Package.Sub_Package`；为了成功导入`Sub_Package`下的模块，同理需要在`Sub_Package/__init__.py`中显式导入相应子模块。

```python
# Package/Sub_Package/__init__.py
from . import module_a
from . import module_b
```

于是，对子包中的模块的测试结果如下：

```python
# test.py
import Package
print(Package.Sub_Package.module_b.x) # 2
```

## 子包中的导入问题

子包中同级模块的导入，例如`Sub_Package`下`module_b`导入`module_a`，可能有以下三种方式：

**import module_a**

```python
# Package/Sub_Package/module_b.py
import module_a
x = module_a.x + 1
if __name__ == '__main__':
    print(x) # 2

# test.py
import Package
print(Package.Sub_Package.module_b.x) # No module named 'module_a'
```

子模块调用时入口`module_b`可以正确找到同级的`module_a`，而`test.py`中入口在`Package`，故无法正确找到`module_a`。

**from . import module_a**

这是相对导入方式，可以解决上述问题。然而，子模块内运行却出错。这是因为**相对导入方式仅能应用于包**，而Python解释器识别包的的两个条件：
- 文件夹中必须有`__init__.py`文件
- 不能作为顶层模块来执行该文件夹中的py文件（即不能作为主函数的入口）

显然，直接运行子模块`module_b.py`违背了条件二。

```python
# Package/Sub_Package/module_b.py
from . import module_a
x = module_a.x + 1
if __name__ == '__main__':
    print(x) # cannot import name 'module_a'

# test.py
import Package
print(Package.Sub_Package.module_b.x) # 2
```

**from Package.Sub_Package import module_a**

这是绝对导入方式。当入口是`Package`包时，自然可以正确识别`Package.Sub_Package`。而直接运行子模块时，显然无法识别了。

```python
# Package/Sub_Package/module_b.py
from Package.Sub_Package import module_a
x = module_a.x + 1
if __name__ == '__main__':
    print(x) # No module named 'Package'

# test.py
import Package
print(Package.Sub_Package.module_b.x) # 2
```

当然也有方法使子模块正常运行——将`Package`所在目录加入系统搜索目录即可。但是，这样的处理却不是必要的，因为`module_b`最终目的是为Package所调用，并不需要直接运行它。因此以上的绝对或者相对调用方式足以满足需求；并且，相对调用方式的通用性更好，因为它不受Package的名称所影响。

```python
# Package/Sub_Package/module_b.py
import os
import sys
script_path = os.path.abspath(__file__) # 当前module绝对路径
package_path = os.path.dirname(os.path.dirname(os.path.dirname(script_path))) # 上三级路径，即Package的父目录
sys.path.append(package_path) # 加入默认搜索路径列表

from Package.Sub_Package import module_a
x = module_a.x + 1

if __name__ == '__main__':
    print(x) # 2
```

## 总结

- `__init__.py`表明所在文件夹为Package，并且在import该Package时会被执行
- `__init__.py`中定义`__all__`指明模糊导入的模块或变量
- 针对`import package`的导入方式，需要在`__init__.py`文件中导入子模块/子包
- 注意使用相对/绝对导入方式导入子模块 