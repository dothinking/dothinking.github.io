---
categories: [python/vba/cpp]
tags: [python]
---

# 使用subprocess模块调用子进程并获取输出


---

从python2.4开始，内置的`subprocess`模块可以创建子进程并连接子进程的标准输入/输出/错误，因此可以用来执行外部程序并获取执行结果和输出。本文示例基于Python2.7，转为Python3代码时需要考虑对`bytes`类型返回值的`decode()`转码。

## Popen类方法

`subprocess`模块通过`Popen`类完成创建子进程并与其交互的功能，常见的几个成员函数如下：

-  `Popen.poll()`检查子进程是否已经结束，未结束返回`None`，结束返回`returncode`属性值
-  `Popen.wait()`，`Popen.communicate()`都会阻塞父进程，直到子进程结束
-  `Popen.communicate(input=None)`与子进程交互：向`stdin`发送数据，从`stdout`和`stderr`读取数据

**创建`Popen`对象后，主程序不会自动等待子进程完成**。

以上三个成员函数都可以用于等待子进程返回：`while`循环配合`Popen.poll()`、`Popen.wait()`、`Popen.communicate()`。由于后面二者都会阻塞父进程，所以无法 **实时** 获取子进程输出，而是等待子进程结束后一并输出所有打印信息。另外，`Popen.wait()`、`Popen.communicate()`分别将输出存放于管道和内存，前者容易超出默认大小而导致死锁，因此不推荐使用。

## Popen类属性

`Popen`类具有三个与输入输出相关的属性：`Popen.stdin`, `Popen.stdout`和`Popen.stderr`，分别对应子进程的标准输入/输出/错误。Python的`sys`模块定义了标准输入/输出/错误：

``` python
sys.stdin  # 标准输入
sys.stdout # 标准输出
sys.stderr # 标准错误信息    
```

以上三个对象类似于文件流，因此可以使用`readline()`和`write()`方法进行读写操作。例如打印标准输出的`print`指令等效于`sys.stdout.write()`。

需要注意的是，除了直接向控制台打印输出外，标准输出/错误的打印存在缓存，为了实时输出打印信息，需要执行

``` python
sys.stdout.flush()
sys.stderr.flush()
```

## 标准输入/输出/错误参数

`Popen`类构造函数中的三个参数`stdin`, `stdout`和`stderr`用以指定执行程序的标准输入/输出/错误的文件句柄。它们的值可以是`PIPE`、文件描述符(正整数)、文件对象或`None`：

- `PIPE`表示创建一个连接子进程的新管道，默认值`None`, 表示不做重定向。
- 子进程的文件句柄可以从父进程中继承得到。
- `stderr`可以设置为`STDOUT`，表示将子进程的标准错误重定向到标准输出。

参考示例：

``` python
 import subprocess

 child1 = subprocess.Popen(["ls","-l"], stdout=subprocess.PIPE)
 child2 = subprocess.Popen(["wc"], stdin=child1.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
 out = child2.communicate()
```

其中，`subprocess.PIPE`为文本流提供一个缓存区，child1的`stdout`将文本输出到缓存区；随后child2的`stdin`从该`PIPE`读取文本，child2的输出文本也被存放在`PIPE`中，而标准错误信息则重定向到标准输出；最后，`communicate()`方法从`PIPE`中读取child2子进程的标准输出和标准错误。

## 示例

假设被调用的Python代码如下，其中的`flush()`方法作用为及时清空缓存，以便主程序实时获取其输出信息。

``` python
# coding:utf-8
# file: called.py
import time, sys
try:
    # 获取标准输入
    N = int(sys.stdin.readline())   
except ValueError:
    # 标准错误信息
    sys.stdout.write("numeric input required!!\n")
    sys.stdout.flush()
    exit(1)
else:
    for i in range(N):
        # 标准输出
        sys.stdout.write("%d\n" %i)     
        sys.stdout.flush()
        time.sleep(1)
    exit(0)
```

主程序`call.py`：

``` python
import subprocess, shlex
command = "python called.py"
p = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# 为子进程传递参数
p.stdin.write('5\n') 
# 实时获取输出
while p.poll() == None:
    out = p.stdout.readline().strip()
    if out:
        print "sub process output: ", out
# 子进程返回值
print "return code: ", p.returncode
```

- `stdin=subprocess.PIPE`指定子程序输入方式，接着由`p.stdin.write('5\n')`给定；子程序中使用`sys.stdin.readline()`获取
- `stderr=subprocess.STDOUT`将标准错误重定向到标准输出，于是可以使用`p.stdout.readline()`统一获取标准输出和标准错误信息

---

## 参考资料

- [17.1. subprocess — Subprocess management](https://docs.python.org/2/library/subprocess.html)
- [python子进程模块subprocess详解](https://hacpai.com/article/1462524113048)
- [python子进程模块subprocess详解与应用实例 之三 ](http://blog.chinaunix.net/uid-26000296-id-4461555.html)
- [Python中print如何刷新缓冲立刻打印输出结果](http://www.revotu.com/how-to-flush-output-of-python-print.html)