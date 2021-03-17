
# [格致](https://dothinking.github.io/)：基于[MkDocs](https://www.mkdocs.org/)搭建的个人博客

* `Markdown`语法编辑文章
* 支持`Latex`公式（MathJex）
* 按年份归档文章
* 自动部署到`Github Page`


## 使用

- 修改[mkdocs.yml](./mkdocs.yml)定义博客信息
- 在[docs](./docs)文件夹下创建文章。为便于自动按年份归档，文件名格式`yyyy-mm-dd-xxx.md`
- 提交更新到远程`master`分支，触发`Github Action`自动部署
    - 根据[docs](./docs)下文件名生成按年份归档信息
    - 构建博客内容并上传到远程`gh-pages`分支



## 本地调试

安装Python及以下第三方库

```bash
$ pip install mkdocs
$ pip install pymdown-extensions
```

执行`make`命令（等效为创建归档信息并执行`mkdocs serve`）

```bash
$ make serve
```

通过浏览器访问`127.0.0.1：8000`