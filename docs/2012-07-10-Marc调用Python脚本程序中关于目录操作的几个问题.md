---
categories: [finite element analysis]
tags: [Marc, python]
---

# Marc调用Python脚本程序中关于目录操作的几个问题

---

本文为作者在编写供`Marc`调用的`Python`脚本程序过程中，遇到的关于当前目录的几个问题及解决方法。


## 需求

通过Python脚本为Marc读入初始化数据，目录结构如下所示：


    user_application
    |- data
    |  |- initial_data.txt
    |-menu_command
    |  |- marc_menu_newproject.py

其中，`initial_data.txt`为初始数据，`marc_menu_newproject.py`为脚本文件。

基本思路为：

1. 获取当前脚本文件所在目录的上级目录，即`data`文件夹所在目录
2. 用Marc内部命令`*user_defined_read filename`读取`data`下文件

```python
user_dir = os.path.dirname(os.getcwd()) # 脚本目录
data_dir = user_dir + "\\data\\initial_data.txt"
```


## ImportError: No module named os

当前Python版本为Marc安装时自带的Python 2.5，但是在python编辑器下直接运行`import os`不存在此问题。猜测原因为：实际调用Python脚本的是Marc程序，则由于Marc无法搜索到Python的`os`模块而导致错误。

**解决方案**：为Marc指定Python相关模块，即建立`PYTHONPATH`环境变量[^1]，其值为Marc安装目录下Python库文件路径`Lib`。

至此，第一个问题解决。

## 读入初始文件失败

数据文件的目标位置是`\user_application\data\`，实际上却定位向了错误位置`C:\User\data\`。这是因为上述代码期望通过`os.getcwd()`获取当前脚本文件所在目录，然而`os.getcwd()`获取的是当前目录——正在运行的Marc程序的目录，而不是Marc调用的脚本的目录[^2]。

**解决方案**：使用`sys.path[0]`获取当前脚本文件所在路径[^3]。

因此，修正后代码为：

```python
user_dir = os.path.dirname(sys.path[0]) # 脚本目录
data_dir = user_dir + "\\data\\initial_data.txt"
```


[^1]: [Windows下配置Python环境变量](http://www.cnblogs.com/qiyeshublog/archive/2012/01/24/2329162.html)

[^2]: [Python语言获取脚本文件所在路径](http://blog.csdn.net/bupteinstein/article/details/6534177)

[^3]: [Python 获取当前脚本文件路径目录](http://www.cnblogs.com/pchgo/archive/2011/09/19/2181248.html)