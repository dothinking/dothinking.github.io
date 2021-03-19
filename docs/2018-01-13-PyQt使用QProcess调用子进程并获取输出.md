---
categories: [python/vba/cpp]
tags: [python,PyQt]
---

# PyQt使用QProcess调用子进程并获取输出


---

`QProcess()`类可以创建子进程执行外部程序，使用`readyReadStandardOutput`信号监听子进程中的标准输出事件，使用`readAllStandardOutput()`读取子进程标准输出；对标准错误的操作同理。本文基于Python3和PyQt5示例以上流程的代码。

## 创建QProcess并关联监听事件

``` python
self.process = QProcess()
self.process.readReadStandardOutput.connect(self.addStdOut)
self.process.readReadStandardError.connect(self.addStdErr)
self.process.finished.connect(self.stop)
```

## 启动子程序

```python
self.process.start("command_line")
```

## 响应槽函数

```python
def addStdOut(self):
    output = bytes(self.process.readAllStandardOutput()).decode()
```

`readAllStandardOutput()`返回的是Qt的`QbyteArray`类型数据，对应Python的`bytes`，二者可以直接转换。然后使用`bytes`类型对象的`decode()`方法转为python的`str`。