---
layout: post
author: Train
description: GitLab持续集成介绍
keywords: GitLab, CI CD
tags: GitLab
---

# GitLab CI/CD：功能介绍

---

持续集成（Continuous Integration）是为了配合敏捷开发的速度和效率而产生的一个用于编译、测试、发布、部署的工具。开发人员的每一次代码提交，都将触发预先定义的任务，自动进行编译、测试、部署等。如果成功则接受这次提交，否则提示集成失败。本篇介绍GitLab提供的持续集成（CI/CD）功能。

## 基本流程

自GitLab 8.0版本起，`Continuous Integration`功能被集成到GitLab基本配置中，并且默认对所有项目生效。两步实现GitLab的CI/CD服务 [^1]：

- 在代码仓库根目录创建`.gitlab-ci.yml`文件
- 配置执行任务的`Runner`

`.gitlab-ci.yml`文件按照`YAML`文件格式定义了需要自动化执行的任务列表，每个任务由一系列命令行代码完成；`Runner`是GitLab默认配置好的服务器（一般是Linux环境），或者自行手动添加的服务器（例如自己的主机）。

通过提交代码等触发CI/CD服务后，GitLab按一定原则分配`Runner`。注意每个任务都将被分配给一个具备相对独立环境的`Runner`，即便两个任务被先后分配到了同一个`Runner`。

`Runner`接到任务后，将远程仓库下载到`Runner`本地，然后执行该任务定义的指令。


## 测试案例一

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


## 测试案例二

案例一仅仅作为示意，实际操作中更多的是针对同一个工程定义`build`和`test`阶段的`job`。注意到每个`job`都是独立的：

- 同一工程的两个`job`可能被分配到不同的`Runner`上执行
- 即便定义了相同的`Runner`，执行任务之前 **默认** 都执行了`git clean`，也就是默认从相同的状态开始执行`build`和`test`阶段的任务

但是，实际操作中我希望`build`阶段的任务编译完成的工程，例如动态链接库文件，可以直接用于`test`阶段的任务；而非在`test`阶段的任务中又重新编译一遍。

这就需要用到`artifacts`和`dependencies`，示例二：

```yaml
variables:
  PROJECT: $CI_PROJECT_NAME
  BRANCH: $CI_COMMIT_REF_NAME
  TAG: $CI_COMMIT_TAG
  REF: $CI_COMMIT_SHA

# stages
stages:
  - build
  - test

# jobs
build:
  stage: build
  script:
    - make build
  artifacts:
    paths:
      - dist/
    expire_in: 1 hour
  tags:
    - xxxx

test:
  stage: test
  dependencies:
    - build
  script:
    - make test
  tags:
    - xxxx
```

注意两处细节：

- `build`阶段的任务将`dist`目录下的所有文件作为`artifacts`
- `test`阶段的任务将`build`任务作为`dependencies`

其效果是`build`的`artifacts`也就是`dist`，将在`test`阶段仓库初始化完成后下载到工作目录下。因此，`test`任务可以直接使用`build`完成的文件。

下面列出了执行`test`任务过程中相应的日志信息：

    Downloading artifacts for build (20220274)...
    Runtime platform                                    arch=amd64 os=windows pid=24332 revision=577f813d version=12.5.0
    WARNING: Failed to load system CertPool: crypto/x509: system root pool is not available on Windows 
    Downloading artifacts from coordinator... ok        id=20220274 responseStatus=200 OK token=xxxxx



## 自定义Runner

以上任务使用通用环境即可完成，例如`g++`编译和`python`环境，但有时可能需要特定的环境，例如`Visual Studio`或者第三方库如`NXOpen C++`，此时需要配置专用的服务器。GitLab提供了Linux/MacOS/Windows等一系列平台的配置方法 [^3]。

流程很简明：下载`gitlab-runner`文件，注册`Runner`，安装和启动服务。配置成功后即可在仓库的`Settings->CI/CD->Runners->Specific Runners`下发现自己的`Runner`，注意设置`tag`以便可以在`.gitlab-ci.yml`中指定在此`Runner`执行任务。

### 设置`git bash`为默认的`shell`

Windows系统的`GitLab Runner`默认以`Powershell`作为运行的`shell`，但我们有时更倾向于使用`git bash`。具体做法为修改`gitlab-runner.exe`同目录下的配置文件`config.toml`：

    concurrent = 1
    check_interval = 0

    [session_server]
    session_timeout = 1800

    [[runners]]
    name = "Example Server"
    url = "https://xxx.yyy.com/"
    token = "xxxx"
    executor = "shell"
    shell = "bash"
    builds_dir="/path/to/runner/builds/"
    [runners.custom_build_dir]
    [runners.cache]
        [runners.cache.s3]
    [runners.cache.gcs]

1. 暂停gitlab-runner服务，备份原始config.toml
2. 将原始文件的`shell = "powershell"`行修改为：
    - `shell`切换为`bash`，注意确保`git bash`已经添加到`PATH`环境变量中
    - `builds_dir`切换为`gitlab-runner.exe`所在目录下的`builds`，注意采用Linux的路径分隔符 [^4]
3. 启动gitlab-runner服务

## 总结

- 在仓库根目录`.gitlab-ci.yml`文件中定义任务，提交代码触发`CI/CD`服务，自动在共享或者自定义的`Runner`上依次执行任务
- `Runner`克隆远程仓库到本地->清除未追踪的文件->执行自定义脚本
- `job`定义中的`tags`关键字可以筛选`Runner`，仅分配该任务到具备指定`tag`的`Runner`服务器
- `artifacts`和`dependencies`实现跨任务级别共享文件
- 如果通用`Runner`不能满足开发环境需求，可以添加自定义`Runner`



[^1]: [Getting started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/README.html)
[^2]: [GitLab CI/CD Pipeline Configuration Reference](https://docs.gitlab.com/ee/ci/yaml/README.html)
[^3]: [Install GitLab Runner](https://docs.gitlab.com/runner/install/)
[^4]: [Windows GitLab CI Runner using Bash](https://stackoverflow.com/questions/41733406/windows-gitlab-ci-runner-using-bash)