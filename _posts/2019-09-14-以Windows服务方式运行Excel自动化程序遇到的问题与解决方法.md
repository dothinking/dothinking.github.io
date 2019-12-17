---
layout: post
author: Train
description: Windows Service执行Excel自动化程序
keywords: python, win32com, gitlab-runner
tags: [python, VBA]
---

利用[前文]({{ site.baseurl }}{% post_url 2019-04-21-Python win32com模块操作Excel的几个应用 %})记录的Python操作Excel的示例代码，可以进行Excel的自动化操作，例如Excel VBA的自动化测试；将其作为Windows服务运行，则可以方便为网络中的其他机器调用。本文正是记录配置Excel自动化服务过程中遇到的问题与相应解决措施。

## 问题描述

最近有个需求是对启用宏的Excel 2010文件的自动化测试，需要配置在服务器上以供`GitLab-Runner`调用。于是，按照读入测试数据、执行测试VBA、验证计算结果的逻辑写好Python脚本，调试通过后在本地运行一切正常。然而，通过Commit提交触发CI/CD流程，即`GitLab-Runner`以Windows服务的方式执行相同的脚本时，却出现了各种各样的问题。

根本原因显然是**本地账户**和**系统服务**执行Excel自动化操作上的差异，以下逐一记录遇到的问题。除了部分与Python相关的问题外，其余应该具备通用性，可作为Windows服务方式执行Excel、Word、Outlook等自动化程序出现问题时的参考。

**当前登陆账户具备管理员权限**。


## 问题与解决方法


### 1. Open method of Workbooks class failed

```
(-2147352567, 'Exception occurred.', (0, 'Microsoft Excel', 'Open method of Workbooks class failed', 'xlmain11.chm', 0, -2146827284), None)
```

在Stackoverflow搜索到了这个问题的解决方法[[^1]]，根据Windows位数在目标目录创建一个`Desktop`文件夹：

- 64位系统： `C:\Windows\SysWOW64\config\systemprofile\`
- 32位系统： `C:\Windows\System32\config\systemprofile\`

虽然暂时解决了问题，却也不知是何缘由。经历后来遇到的问题4才明白：Excel需要有`Interactive User`登陆才能正常运行，上面的步骤正是为其提供了用户“桌面”；然而一旦需要更多用户账户相关的设置时，就会有新的问题出现了。


### 2. Programmatic access to Visual Basic Project is not trusted

```
(-2147352567, 'Exception occurred.', (0, 'Microsoft Excel', 'Programmatic access to Visual Basic Project is not trusted\n', 'xlmain11.chm', 0, -2146827284), None)
```

这个问题很明显，一旦代码需要访问VBA工程对象，例如访问`module`对象、Python动态执行VBA代码，则需要相应的许可（Excel软件信任区设置中有该选项）。

解决方法可以是利用Python动态修改相应注册表项和值来允许访问VB工程，或者参考[[^2]]手工永久设置。


### 3. 执行VBA代码超时

这一般是因为VBA代码中存在错误。因为本文的自动化过程是由Python驱动的，一旦VBA代码出错而被挂起，Python就无法得到响应了。

针对本文应用场景的解决方案是在VBA测试代码的开头加上一句`On Error Resume Nest`，即忽略VBA代码中的错误，以便Python可以正常执行后续流程。并且无需担心此举造成的错误，VBA代码存在错误必将导致后续验证输出的失败，也就表明了这个测试案例必将失败。


### 4. 无法正确加载VBA中调用的C++动态链接库

这个问题是从问题3中排查出来的——正是无法正确加载DLL才导致了VBA测试代码出错。VBA代码中直接通过文件名引用DLL，而DLL所在路径已经添加到了`PATH`环境变量中。由此看来，以系统服务方式启动的Excel并不能正确获取到环境变量。

```vb
Declare Function xxx Lib "sample_dll_name.dll" ( arguments_list_xxx ) As xxx
```

解决方法为通过`DCOMConfig`设置启动Excel的用户[[^3], [^4]]：

1. `Windows+R` -> `dcomcnfg`，打开`Component Service`
2. `Console Root` -> `Component Services` -> `My Computer` -> `DCOM Config`
3. 从`DCOM Config`中找到`Microsoft Excel Application`，右键选择`Properties`
    - 选择`Identity`选项卡，选择`the launching user`，表示以登陆用户来启动Excel（这里可能会出现新的问题，参见问题5）
    - 选择`Security`选项卡，为指定的账户自定义`Launch and Activation Permissions`和`Access Permissions`

如果上述`DCOM Config`列表中并不存在`Microsoft Excel Application`，则参考下面步骤[[^4]]：以64位Windows系统上的32位Excel为例，

1. `Windows+R` -> `mmc -32`打开`Microsoft Managemant Console`
2. `File` -> `Add Remove Snap-in` -> `Component Services` -> `Add` -> `OK`添加`Component Services`
3. 按`DCOMConfig`步骤2，3进行设置


### 5. The configured identity is incorrect

```
(-2147467238, 'The server process could not be started because the configured identity is incorrect. Check the username and password.', None, None)
```

到目前为止一切正常，可一旦服务器进入待机状态，就出现了上述错误。原因也很明确，因为处理问题4时设置了以当前账户来运行Excel，于是当前用户退出时系统尝试再次登陆，但我们并没有设置任何登陆口令。

解决方法为`DCOMConfig`设置`Identity`为`This User`，然后输入用户名和密码（注意域内用户需要带上域名称，例如`domain\user`）[[^5]]。

后来问题7的出现表明这只是其中一个解决方案。


### 6. Module has no attribute 'CLSIDToClassMap'

```
module 'win32com.gen_py.00020813-0000-0000-C000-000000000046x0x1x7' has no attribute 'CLSIDToClassMap'
```

这是`win32com`以`EnsureDispatch()`方式启动Excel会产生临时文件夹，出现此问题后只要删除相应文件夹即可，即本例中的`00020813-0000-0000-C000-000000000046x0x1x7`。

```python
import win32com.client    
app = win32com.client.gencache.EnsureDispatch('Excel.Application')
```

那么如何找到该目录呢？如下代码将打印目标位置[[^6]]：

```python
import win32com
print(win32com.__gen_path__)
```

- 对于本地账户执行的代码：`C:\Users\<my username>\AppData\Local\Temp\gen_py`
- 对于系统服务执行的代码：`C:\Windows\Temp\gen_py`

*如果`GitLab-runner`是系统服务以本地账户形式运行的（如问题8解决方案的情况），则同样对应本地账户目录而非系统目录。*


### 7. This COM object can not automate the makepy process - please run makepy manually for this object

与问题6删除缓存相反，这个错误表明无法自动产生`gen_py`文件夹，而这正是`win32com`以`EnsureDispatch()`方式启动Excel所必须的。所以按照提示，手动运行`makepy.py`即可。

1. 在`Lib\site-packages\win32com\client`目录下执行`python makepy.py -d`
2. 在弹出的`select library`对话框中选择Excel相关的项目即可，例如`Microsoft Excel 16.0 Object Library (1.9)`
3. 用户`Temp`文件夹下即可产生`gen_py`文件夹

### 8. Cannot use object linking and embedding

在正常工作了几天后，突然出现了此问题，具体原因尚不明确。实际上，这是本地账户打开Excel时的错误提示，在`GitLab-Runner`上执行Excel自动化脚本时表现为失去响应直至超时，即卡在打开Excel工作簿上。

解决方法为通过`DCOMConfig`设置`Identity`为`The launching user`[[^7]]。

然而，这就与问题5冲突了！索性问题5还有一个替代方案，`GitLab-Runner`允许设置登陆账户，我们可以将其从默认的`Local System`切换到`This account`，同理设置`domain\user`及其登陆密码。

1. `Windows+R` -> `services.msc` -> `gitlab-runner` -> `properties`
2. `Log On` -> `This account` -> 填写`Password`和`Confirm Password`


另外，MSDN上也有人给出了保持`DCOMConfig`中`This account`不变而修改本地Excel文件`Security`属性的解决方法[[^8]]，本文尚未是测试。

---

[^1]: [1] [excel access denied with win32 python pywin32](https://stackoverflow.com/questions/17177612/excel-access-denied-with-win32-python-pywin32?answertab=votes#tab-top)
[^2]: [2] [Microsoft Project – how to control Macro Settings using registry keys](https://blogs.technet.microsoft.com/diana_tudor/2014/12/02/microsoft-project-how-to-control-macro-settings-using-registry-keys/)
[^3]: [3] [How to configure Office applications for automation from a COM+/MTS package](https://theether.net/download/Microsoft/kb/288368.html)
[^4]: [4] [Running excel from a windows service](https://bharathkumaran.wordpress.com/2011/10/25/running-excel-from-a-windows-service/)
[^5]: [5] [Excel COM automation via interactive user stops working when user logs off](https://stackoverflow.com/questions/4234615/excel-com-automation-via-interactive-user-stops-working-when-user-logs-off)
[^6]: [6] [python-win32com excel com model started generating errors](https://stackoverflow.com/questions/52889704/python-win32com-excel-com-model-started-generating-errors)
[^7]: [7] [Cannot use object linking and embedding - EXCEL 2007 - DCOM](https://social.msdn.microsoft.com/Forums/en-us/9d38aad5-4a61-4edc-9645-c76610756940/cannot-use-object-linking-and-embedding-excel-2007-dcom?forum=innovateonoffice)
[^8]: [8] [Cannot use object linking and embedding Excel 2007](https://social.msdn.microsoft.com/Forums/en-US/251a6e4a-e4ef-45a6-8b73-91dc4620eedf/cannot-use-object-linking-and-embedding-excel-2007?forum=exceldev)
