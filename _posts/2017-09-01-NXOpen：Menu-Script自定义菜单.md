---
layout: post
author: Train
description: NXOpen按模块显示自定义菜单
keywords: NX, NXOpen, MenuScript
tags: [NX, NXOpen]
---

NX自定义菜单栏可以根据当前所在的不同模块而显示不同内容，本文记录创建按模块显示的菜单栏的基本流程。以自定义菜单`TEST MENU`为例，该菜单包含三个分组：`Public`、`Modeling`和`FEM`。其中，

- `Public`分组显示在任意模块下
- `Modeling`及`FEM`分组仅在`Modeling`或`Pre/Post`模块显示
- `Modeling`分组在`Modeling`和`Pre/Post`模块显示不同的菜单项，`FEM`分组同理

示例效果参考：

<div align='center'><img src="{{ "/images/2017-09-01-01.png" | prepend: site.baseurl }}"></div>


## 主菜单

文件夹`Startup`中创建的菜单脚本文件将在NX启动时进行加载，即可以显示在任意模块下。本例中需要按照不同模块加载，则需要`APPLICATION_BUTTON`命令指定加载的菜单文件。主菜单文件`test_main.men`代码：

```
VERSION 170
EDIT UG_GATEWAY_MAIN_MENUBAR

!-------------------------------------------------
! user defined menu
!-------------------------------------------------
BEFORE UG_HELP
    CASCADE_BUTTON TEST_MENU
    LABEL TEST MENU
END_OF_BEFORE

!-------------------------------------------------
! contents of user defined menu
! ------------------------------------------------

! public menus show in all applications
MENU TEST_MENU
    BUTTON TEST_MENU_PUBLIC
    LABEL Public Button
END_OF_MENU


! Application dependent menus show 
! in specified application
MODIFY
    APPLICATION_BUTTON UG_APP_MODELING
    MENU_FILES test_modeling.men
END_OF_MODIFY

MODIFY
    APPLICATION_BUTTON UG_APP_SFEM
    MENU_FILES test_fem.men
END_OF_MODIFY
```

其中，`TEST_MENU_PUBLIC`按钮对任意模块生效，`test_modeling.men`和`test_fem.men`是模块相关的菜单脚本文件，分别控制`TEST MENU`在`Modeling`模块、`Pre/Post`模块下的显示内容。**模块菜单**将在第二部分介绍。

根据MenuScript语言基本规则，**使用.menu脚本可以创建基本的菜单项命令，分类组织基本菜单项命令到.tbr脚本即为工具条，按Group组织工具条.tbr文件则形成新版的Ribbon界面**。因此，为了实现开始所述`Public`、`Modeling`和`FEM`三个分组，需要分别创建三个工具条文件，例如`test_public.tbr`、`test_modeling.tbr`及`test_fem.tbr`。**模块分组**将在第三部分介绍。

考虑到新版的Ribbon界面，可以在`Startup`文件夹下创建`test_main.rtb`，主要内容即为`TEST MENU`的三个分组工具条文件：

```
!-------------------------------------------------
! scripts for new style RIBBON UI!
! toolbar files will be transfered to ribbon groups
!-------------------------------------------------
TITLE TEST MENU
VERSION 170

GROUP test_public.tbr
GROUP test_modeling.tbr
GROUP test_fem.tbr
```

## 模块菜单

**按模块加载的菜单脚本存放于`Application`文件夹下**。

除了`Gateway`中定义的菜单项命令之外，NX还将按当前模块加载相应菜单脚本中定义的菜单项命令，共同组成`TEST MENU`。根据图1，本例的模块菜单脚本文件参考：

```
! test_modeling.men

VERSION 139
EDIT UG_GATEWAY_MAIN_MENUBAR

!-------------------------------------------------
! user defined menu
!-------------------------------------------------
BEFORE UG_HELP
    CASCADE_BUTTON TEST_MENU
    LABEL Main test menu
END_OF_BEFORE

!-------------------------------------------------
! contents of user defined menu
! ------------------------------------------------
MENU TEST_MENU

    SEPARATOR

    BUTTON TEST_MENU_MODELING_1
    LABEL Modeling Button 1
    BUTTON TEST_MENU_MODELING_2
    LABEL Modeling Button 2
    BUTTON TEST_MENU_MODELING_3
    LABEL Modeling Button 3

    SEPARATOR

    BUTTON TEST_MENU_FEM_1
    LABEL FEM Button 1
END_OF_MENU
```

```
! test_fem.men

VERSION 139
EDIT UG_GATEWAY_MAIN_MENUBAR

!-------------------------------------------------
! user defined menu
!-------------------------------------------------
BEFORE UG_HELP
    CASCADE_BUTTON TEST_MENU
    LABEL Main test menu
END_OF_BEFORE

!-------------------------------------------------
! contents of user defined menu
! ------------------------------------------------
MENU TEST_MENU

    SEPARATOR

    BUTTON TEST_MENU_MODELING_1
    LABEL Modeling Button 1

    SEPARATOR

    BUTTON TEST_MENU_FEM_1
    LABEL FEM Button 1
    BUTTON TEST_MENU_FEM_2
    LABEL FEM Button 2
END_OF_MENU
```

## 按模块分组

如第一部分所述，`Public`、`Modeling`和`FEM`三个分组分别对应了`test_public.tbr`、`test_modeling.tbr`和`test_fem.tbr`三个工具栏文件，因此这一部分来实现它们。

根据开始设定的需求，`Public`为公共分组，因此在`Startup`下创建脚本文件`test_public.tbr`，内容即为菜单脚本`test_main.men`中定义好的菜单项命令：

```
TITLE PUBLIC
VERSION 170

BUTTON TEST_MENU_PUBLIC
```

对于按模块加载的分组`Modeling`和`FEM`，需要存放于`Application`下的特定目录：

- `Profiles/UG_APP_MODELING/`下的工具条文件将在`Modeling`环境下加载，
- `Profiles/UG_APP_SFEM/`下的工具条文件将在`Pre/Post`环境下加载。

因此在`Profiles/UG_APP_MODELING/`下创建`test_modeling.tbr`和`test_fem.tbr`，其内容来自`test_modeling.men`中定义好的四个命令：`TEST_MENU_MODELING_1-TEST_MENU_MODELING_3`和`TEST_MENU_FEM_1`。显然，前三个属于`Modeling`分组，最后一个属于`FEM`分组。因此，分别分类写入`test_modeling.tbr`和`test_fem.tbr`：

```
! test_modeling.tbr

TITLE MODELING
VERSION 170

BUTTON TEST_MENU_MODELING_1
BUTTON TEST_MENU_MODELING_2
BUTTON TEST_MENU_MODELING_3
```

```
! test_fem.tbr

TITLE FEM
VERSION 170

BUTTON TEST_MENU_FEM_1
```


同理在`Profiles/UG_APP_SFEM/`下创建`test_modeling.tbr`和`test_fem.tbr`：

```
! test_modeling.tbr

TITLE MODELING
VERSION 170

BUTTON TEST_MENU_MODELING_1
```

```
! test_fem.tbr

TITLE FEM
VERSION 170

BUTTON TEST_MENU_FEM_1
BUTTON TEST_MENU_FEM_2
```

## 总结


以上即为按模块加载的自定义菜单的基本创建流程，简要归纳为：

- 在主菜单文件中定义公共菜单项或者指定按模块加载的菜单文件
- 在按模块加载的菜单文件中定制相应的菜单项
- 组织所有菜单项命令为相应的分组，默认分组位于`startup`，按需加载分组位于`application/profiles`


最后，本文涉及菜单脚本汇总于[nx_menu_script](https://github.com/dothinking/blog/tree/master/src/nx_menu_script)，并将其基本流程图示如下：

<div align='center'><img src="{{ "/images/2017-09-01-02.png" | prepend: site.baseurl }}"></div>

