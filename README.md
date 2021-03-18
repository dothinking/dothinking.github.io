
# [格致](https://dothinking.github.io/)：基于[MkDocs](https://www.mkdocs.org/)搭建的个人博客


* 采用`Markdown`语法编辑文章

* 支持`Latex`公式（MathJex）

* 按分类/年份归档文章

* 自动部署到`Github Page`


## 使用

- 修改[mkdocs.yml](./mkdocs.yml)和[about.md](./docs/about.md)定义博客信息

- 修改[extra.css](./docs/css/extra.css)自定义样式（可选，覆盖`mkdocs`主题默认样式）

- 在[docs](./docs)文件夹下创建文章

    - 为便于自动按年份归档，文件名格式`yyyy-mm-dd-title.md`
    - 为便于自动分类文章，提供元信息`categories`
    - 文章基本结构（元信息、标题为可选项）

            ---
            categories: [foo, bar, ...]
            tags: [this, that, ...]
            ---

            # title

            ---

            markdown-content

            ...

- 提交更新到远程`master`分支，触发`Github Action`自动构建和部署
    - 创建主页（如果[docs](./docs)下不存在`index.html`）
    - 根据[docs](./docs)下文件名生成按年份归档页面
    - 根据文章元信息`categories`生成分类页面
    - 构建博客内容并上传到远程`gh-pages`分支



## 本地调试

安装Python及以下第三方库

```bash
$ pip install mkdocs
$ pip install pymdown-extensions
```

执行`make`命令：


- 调试模式（等效为创建归档/分类页面后执行`mkdocs serve`）

        $ make serve

    通过浏览器访问`127.0.0.1:8000`

- 构建静态页面（等效为创建归档/分类页面后执行`mkdocs build`）

        $ make build