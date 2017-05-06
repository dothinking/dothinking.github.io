---
layout: post
author: Train
description: Selenium Python基本操作
keywords: selenium, phantomjs, chrome
tags: [Python, spider]
---

`Selenium`是一个用于Web应用程序自动化测试的工具，可以模拟人类使用浏览器浏览页面、进行交互的行为。Selenium既支持Chrome、IE、Firefox、Opera等常规浏览器，也支持`PhantomJs`、`HtmlUnit`这类无界面浏览器（headless WebKit）。

Selenium支持.Net、Java、Perl、Python等不同语言编写的测试脚本，本文使用的是Selenium Python。

> Selenium Python bindings provide a convenient API to access Selenium WebDrivers like Firefox, Ie, Chrome, Remote etc.

其帮助手册的项目主页：

> [Selenium with Python](http://selenium-python.readthedocs.io/index.html)

## 安装

使用Selenium Python处理页面前，需要安装Selenium和至少一个WebDriver。本文使用的是Chrome浏览器对应的chromedriver，以及无界面浏览器phantomjs。

1. 使用`pip`安装Selenium Python

```
pip install selenium
```

2. 下载WebDriver（通常是*.exe文件）

Selenium官网给出了一些第三方的WebDriver驱动:

> [Third Party Drivers, Bindings, and Plugins](http://www.seleniumhq.org/download/#thirdPartyDrivers)

下载相应驱动并保存到Python可以识别的目录，例如`C:\Python27\Scripts`。

以上完成了基础工作，本文使用的版本为：

Python | 2.7
Selenium | 3.3.3
Chrome Driver | 2.29
PhantomJS | 2.1

## 定位元素

定位到目标元素后才能进行相应的操作，因此元素定位是以下操作的基础。Selenium提供了如下的元素定位方法：

``` python
find_element_by_id()
find_element_by_name()
find_element_by_xpath()
find_element_by_link_text()
find_element_by_partial_link_text()
find_element_by_tag_name()
find_element_by_class_name()
find_element_by_css_selector()
```

具体参数及使用示例参考文档：

> [Locating Elements](http://selenium-python.readthedocs.io/locating-elements.html)

**一般情况下，查找效率按id, name, css_selector, xpath递减**。

当页面中存在`iframe`时，则需要使用`switch_to.frame()`方法跳转到相应`iframe`，或者使用`switch_to.default_content()`方法切换回顶层结构后，才能使用上述查找方法。示例HTML结构：

``` html
<!DOCTYPE html>
<html>
<head>
    <title>test</title>
</head>
<body>
    <div id='div_id'></div>
    <iframe id="frame_name">
        <html>
        <head>
            <title>frame title</title>
        </head>
        <body>
            <div id='frame_div_id'></div>
        </body>
        </html>
    </iframe>
</body>
</html>
```

示例Python脚本：

``` python
# encoding=utf8
from selenium import webdriver

driver = webdriver.PhantomJS()
driver.get(url)

# 切换到iframe后查找内层元素
driver.switch_to.frame('frame_name') # 参数为iframe的id或者name属性值
frame_div = driver.find_element_by_id('frame_div_id')

# 切换后外层后查找元素
driver.switch_to.default_content()
div = driver.find_element_by_id('div_id')
```


## 获取内容

``` python
# 获取解析后的网页代码
driver.page_source

# 获取元素的内容 / 值
obj = driver.find_element_by_id('id')
print obj.text  # 获取标签内容，对应JQuery中的html()函数
print obj.value # 获取标签值，对应JQuery的val()函数

# 获取元素属性
obj.get_attribute('href')

# 获取元素的css属性
obj.value_off_css_property('font')
```

## 页面输入

主要操作有键盘输入文本，鼠标单击及执行javascript代码：

``` python
# 文本输入
obj.send_keys('something')

# 鼠标单击
obj.click()

# 执行javascript代码
obj.execute_script('alert("hello world")')
```

以上总结了Selenium Python的基本操作，下一篇将具体介绍使用`send_keys()`方法输入文本过程中可能遇到的问题及其解决方法。