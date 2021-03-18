---
categories: [process automation]
tags: [sublime text]
---

# Sublime Text 自定义颜色主题


---

Sublime Text编辑器提供了很多自定义的颜色主题，使代码界面显得更为清晰和优雅。默认颜色主题基本可以满足我们的要求，并且网上也有新的主题可供下载。但是对于喜欢折腾或者为了使选用的主题更符合自己的视觉习惯，有必要新建或者修改颜色主题。

例如，本人比较喜欢默认的Monokai主题，但是对于其灰色显示的注释不太满意，希望可以修改为绿色。

## 当前颜色主题

我们可以从空白文件开始建立自己的主题文件，但是比较有效率的方法是在自己比较感兴趣的主题的基础上，自定义更符合我们习惯的颜色样式。以下步骤可以找到当前颜色主题对应的配置文件：

* 点击`Preferences` => `color scheme`，选择并查看当前颜色主题，确定自己钟意度较大的一款，假设是Monokai。

* 点击`Preferences` => `Browse Packages`，在弹出的窗口中打开`Color Scheme - Default`文件夹，找到`Monokai.tmTheme`文件。

## 自定义样式

将`Monokai.tmTheme`拖到Sublime Text中打开，可以发现是xml格式的，使用键值对定义样式。根据键名即可猜测样式设置的作用，例如注释，查找comment，找到如下一段：


    <dict>
        <key>name</key>
        <string>Comment</string>
        <key>scope</key>
        <string>comment</string>
        <key>settings</key>
        <dict>
            <key>foreground</key>
            <string>#3EE55A</string>
        </dict>
    </dict>


将`<key>foreground</key>`对应的`<string>#3EE55A</string>`修改为需要的颜色即可，例如`#3EE55A`。注意颜色为16进制值，也可以使用一些常规的定义颜色：red green blue white black 等。

其他需要自定义的慢慢查看即可，例如：

* 数字颜色`<string>Number</string>`
* 字符串颜色`<string>String</string>`
* 类颜色`<string>Class name</string>`
* 函数颜色`<string>Function name</string>`

为了避免覆盖掉原来的样式文件，在原有主题的基础上修改完成后，注意另存为一个新的文件。保存的文件名可以自定义，后缀名应该保持不变，例如保存为`MyMonokai.tmTheme`，这样一个新的颜色主题`MyMonokai`就做好了。

## 启用新颜色主题

在`preferences` => `Color Scheme`菜单下可以看到新建的颜色主题`MyMonokai`，选择该主题即可启用。