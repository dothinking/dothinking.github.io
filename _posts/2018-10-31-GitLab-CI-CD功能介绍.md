---
layout: post
author: Train
description: GitLab持续集成介绍
keywords: GitLab, CI CD
tags: GitLab
---

持续集成（Continuous Integration）是为了配合敏捷开发的速度和效率而产生的一个用于编译、测试、发布、部署的工具。开发人员的每一次代码提交，都将触发预先定义的任务，自动进行编译、测试、部署等。如果成功则接受这次提交，否则提示集成失败。本篇介绍GitLab提供的持续集成（CI/CD）功能。

## 基本流程

自GitLab 8.0版本起，`Continuous Integration`功能被集成到GitLab基本配置中，并且默认对所有项目生效。以下是官方提供的一个非常简明实用的入门参考：

> [Getting started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/README.html)

总结为两步实现GitLab的CI/CD服务：

- 在代码仓库根目录创建`.gitlab-ci.yml`文件
- 配置执行任务的`Runner`

`.gitlab-ci.yml`文件按照`YAML`文件格式定义了需要自动化执行的任务列表，每个任务由一系列命令行代码完成；`Runner`是GitLab默认配置好的服务器（一般是Linux环境），或者自行手动添加的服务器（例如自己的主机）。

通过提交代码等触发CI/CD服务后，GitLab按一定原则分配`Runner`。注意每个任务都将被分配给一个具备相对独立环境的`Runner`，即便两个任务被先后分配到了同一个`Runner`。

`Runner`接到任务后，将远程仓库下载到`Runner`本地，然后执行该任务定义的指令。


## 测试案例

为了自动化持续集成，需要确保可以按脚本/命令执行目标任务。例如：

- 在项目中准备好`makefile`，使用`make`或`nmake`编译C++代码
- 准备好单元测试的Python脚本，使用`python -m unittest test_file_name`执行单元测试

以下是GitLab仓库的文件结构，其中`cpp`文件夹用于测试编译C++项目，`python`文件夹用于测试Python单元测试，`.gitlab-ci.yml`即为定义相应任务的文件。

```
Test Project
  +-+cpp
  |   + main.cpp
  |   + makefile
  |
  +-+python
  |   + abs_fun.py
  |   + test.py
  |
  +-+.gitlab-ci.yml
```

示例代码如下：

```cpp
// cpp/main.cpp

#include <iostream>
using namespace std;
int main()
{
    std::cout << "Hello World" << std::endl;
}
```

```
# cpp/makefile
main:main.o
    g++ -o main main.o
```

```python
# python/abs_fun.py
# module to be tested
def ABS(x):
    '''to get absolute value of input'''
    if type(x) in [int, float]:
        return x if x>=0 else -x
    else:
        raise ValueError('Input value should be int or float')
```

```python
# python/test.py
# example for python unit test
import unittest
from abs_fun import ABS

class Test(unittest.TestCase):

    def test_positive(self):
        for x in [1, 1.5]:
            self.assertEqual(ABS(x), x)

    def test_negtive(self):
        for x in [-1, -1.5]:
            self.assertEqual(ABS(x), -x)

    def test_zero(self):
        for x in [0, 0.0]:
            self.assertEqual(ABS(x), x)

    def test_valueerror(self):
        for x in ['123', [123], {'k':123}]:
            with self.assertRaises(ValueError):
                res = ABS(x)
```

如果在本地进行测试，分别在命令行使用`make`和`python -m unittest test`即可。如果要在`Runner`执行，核心指令也是一样的。参考例子：

```yaml
# 定义任务执行阶段
# 默认分为build, test, deploy三个阶段，亦可自定义其他阶段，按顺序执行
# 定义在相同stage的jobs会被并行执行
stages:
  - build
  - test
  - deploy

# 任务列表
# script：必须关键字，即需要执行的指令
# stage：可选，任务所属阶段
# tags：可选，用以筛选Runner，仅考虑将此任务分配给带有相应tag的Runner
job1:
  stage: test
  tags:
    - DOCKER
  script:
    - echo "Python Project Unit Test..."
    - cd ./python
    - python -m unittest test

# 虽然job2定义在job1之后，但job2所属的build阶段在job1的test阶段之前，
# 故job2执行通过后才会执行job1，否则任务失败
job2:
  stage: build
  tags:
    - DOCKER
  script:
    - echo "Building CPP Project from makefile..."
    - cd ./cpp
    - make
    - ./main
```

提交代码触发`CI/CD`功能后即可在`CI/CD->jobs`页面观察执行进度，点击相应任务的`Status`按钮即可观察具体的执行日志：

```
Running with gitlab-runner 11.3.1 (v11.3.1)
  on xxxxx e18fb335
Using Docker executor with image xxxxx ...
Pulling docker image xxxxx ...
Using docker image sha256:1806e9341a6601f388c0666996de0c96b98244d684e6fb52c90c75670a6ec63f for xxxxx ...
Running on runner-e18fb335-project-44214-concurrent-0 via xxxxx...
Cloning repository...
Cloning into '/builds/test_project'...
Checking out 432e5cb0 as master...
Skipping Git submodules setup
$ echo "Building CPP Project from makefile..."
Building CPP Project from makefile...
$ cd ./cpp
$ make
g++    -c -o main.o main.cpp
g++ -o main main.o
$ ./main
Hello World
Job succeeded
```

```
Running with gitlab-runner 11.3.1 (v11.3.1)
  on xxxxx e18fb335
Using Docker executor with image xxxxx ...
Pulling docker image xxxxx ...
Using docker image sha256:1806e9341a6601f388c0666996de0c96b98244d684e6fb52c90c75670a6ec63f for xxxxx ...
Running on runner-e18fb335-project-44214-concurrent-0 via xxxxx...
Cloning repository...
Cloning into '/builds/test_project'...
Checking out 432e5cb0 as master...
Skipping Git submodules setup
$ echo "Python Project Unit Test..."
Python Project Unit Test...
$ cd ./python
$ python -m unittest test
....
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
Job succeeded
```

## 自定义Runner

以上任务使用通用环境即可完成，例如`g++`编译和`python`环境，但有时可能需要特定的环境，例如`Visual Studio`或者第三方库如`NXOpen C++`，此时需要配置专用的服务器。GitLab提供了Linux/MacOS/Windows等一系列平台的配置方法：

> [Install GitLab Runner](https://docs.gitlab.com/runner/install/)

流程很简明：下载`gitlab-runner`文件，注册`Runner`，安装和启动服务。配置成功后即可在仓库的`Settings->CI/CD->Runners->Specific Runners`下发现自己的`Runner`，注意设置`tag`以便可以在`.gitlab-ci.yml`中指定在此`Runner`执行任务。

## 总结

- 在仓库根目录`.gitlab-ci.yml`文件中定义任务如build，uinit test，提交代码触发`CI/CD`服务，自动在共享或者自定义的`Runner`上依次执行任务
- `Runner`克隆远程仓库到本地后执行自定义脚本
- `job`定义中的`tags`关键字可以筛选`Runner`，仅分配该任务到具备指定`tag`的`Runner`服务器
- 如果通用`Runner`不能满足开发环境需求，可以添加自定义`Runner`
