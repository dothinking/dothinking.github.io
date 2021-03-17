---
layout: post
author: Train
description: GitLab Runner清理数据：before_script, after_script
keywords: gitlab-runner
tags: [GitLab]
---

本文记录使用`before_script`和`after_script`解决`GitLab CI/CD`流程中遇到的一个问题。

## 问题描述

在某个项目的`CI/CD`流程中有一个`job`是利用`Python`处理`Excel`和`VBA`，一旦原始`VBA`代码出现模态对话框例如`MsgBox`或者其他用户窗体甚至语法错误，那么整个流程就被堵塞了；接下来要么及时发现后手动取消任务，要么直至任务超时而被自动终止。

无论哪种方式终止任务，其后果都是该`Excel`进程没有被终止。于是在下一次提交任务时，由于进程占用而无法清理出现错误的临时文件（例如下面的`~$example.xlsm`）。

```
Checking out 56485a5a as alpha...
warning: failed to remove dist/example.xlsm: Invalid argument
warning: failed to remove dist/~$example.xlsm: Invalid argument
ERROR: Job failed: exit status 1
```

此时只能登陆`GitLab Runner`服务器，手动终止`Excel`进程。这显然不是一个可以接受的方案，尤其在多人协作的情况下。


## 解决过程


当然，釜底抽薪的方法是`VBA`中避免出现阻塞流程的模态对话框，或者`Python`脚本中检测是否发生阻塞。但前者难以百分百保证（例如`VBA`语法错误），后者有待进一步研究，所以这里给出一个事后的解决思路：

在已经发生因阻塞而异常终止pipeline的情况下，尝试去结束`Excel`进程；并且希望尽量少的改动，例如仅在`.gitlab-ci.yml`中增删几行。

既然是事后方案，我们将联想到`before_script`和`after_script`：

- 本次异常终止后立马使用`after_script`杀掉进程
- 下一次正常提交后使用`before_script`杀掉进程


### 结束`Excel`进程

无论哪种方式，先把终止`Excel`进程的脚本写上。参考文章[[^1]]，在主`makefile`的`cclean`命令中增加一个`kill_excel`。

```makefile
.PHONY: cclean
cclean: kill_excel
	@ echo "do clean work here ..."
	...

.PHONY: kill_excel
kill_excel:
	@if [ -n "`TASKLIST | FINDSTR EXCEL.EXE`" ]; then \
		TASKKILL -F -T -IM EXCEL.EXE ; \
	fi
```

### `after_script`

首先想到的自然是`after_script`——在主要脚本执行完毕之后杀掉`Excel`进程。

```yaml
...
build:
  stage: build  
  script:
    - make build
  after_script:
    - make cclean
  tags:
    - xxxx
...
```

虽然正常情况下，即便任务失败也会继续执行`after_script`。但是，**异常结束（手动取消、超时自动终止）的Pipeline并不会继续执行`after_script`定义的脚本**！

### `before_script`

那就只能考虑`before_script`——在下次正常提交后、开始执行主脚本前进行杀掉`Excel`进程。

```yaml
...
build:
  stage: build
  before_script:
    - make cclean
  script:
    - make build
  tags:
    - xxxx
...
```

但目测还是解决不了问题，因为本文描述的问题出现在准备阶段，尚未来得及执行`script`！

通过输出日志直观了解一下`job`的执行流程：

```
Fetching changes ...
Checking out ...
Downloading artifacts ...
Run before_script ...
Run script ...
Run after_script ...
```

### `Git strategy`

因此有必要学习和参考一下帮助文档[[^2]]中关于`Runner`更新工作目录代码的策略——`GIT_STRATEGY`变量：

- `clone` 每个`job`都克隆一遍仓库，确保项目工作空间总是和仓库代码同步的，因此速度也是最慢的
- `fetch` 重用项目工作空间的代码, 因此速度更快；分为两步：
	- `git fetch`重新获取上一个`job`到当前`job`之间的所有提交
	- `git clean`撤销上一个`job`的任何操作
- `none` 同样重用工作空间，并且跳过所有`git`操作，因此代码不一定是最新的。它的作用在于操作`artifacts`，例如部署前置`job`产生的结果。

从上面的日志可以看出我的`Runner`默认的是`GIT_STRATEGY="fetch"`，并且问题出在`git clean`这一步。

所以，解决思路为暂时不要`git clean`，改为在`before_script`中执行`make cclean`来达到撤销此前`job`操作的目的，同时也顺便杀掉`Excel`进程。

索性`GitLab`果然提供了`git clean`的开关参数`GIT_CLEAN_FLAGS `[[^3]]，将其设置为`none`即可跳过这一步。于是，最终的`.gitlab-ci.yml`（局部）为：

```yaml
...
variables:
  GIT_CLEAN_FLAGS: none
...
build:
  stage: build
  before_script:
    - make cclean
  script:
    - make build
  tags:
    - xxxx
...
```


## 总结

- Pipeline异常结束后并不会执行`after_script`
- 结合`GIT_CLEAN_FLAGS`和`before_script`可以解决本问题

---

[^1]: [1] [How to check if a process is running via a batch script](https://stackoverflow.com/questions/162291/how-to-check-if-a-process-is-running-via-a-batch-script)
[^2]: [2] [Git strategy](https://docs.gitlab.com/ee/ci/yaml/README.html#git-strategy)
[^3]: [3] [Git clean flags](https://docs.gitlab.com/ee/ci/yaml/README.html#git-clean-flags)
