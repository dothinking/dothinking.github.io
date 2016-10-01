---
layout: post
title: hello world
mathjax: true
---

### Image

![Minion]({{ "/_images/test.jpg" | prepend: site.baseurl }})

### MathJax

Let's test some inline math $x$, $y$, $x_1$, $y_1$.

Now a inline math with special character: $\|\psi\rangle$, $x'$, $x^\*$ and $\|\psi_1\rangle = a\|0\rangle + b\|1\rangle$

Test a display math:
$$
   |\psi_1\rangle = a|0\rangle + b|1\rangle
$$
Is it O.K.?

* 示例文章

> to be continue  

*** 

_{{ page.date | date_to_string }}_

# crispy-robot
dead "simple" Medium like blog, 100% hosted on Github

### [demo](http://blog.bigruan.com/crispy-robot)
> sample articles are from [auth0](https://auth0.com/blog)

How to use:

1. git clone https://github.com/ruanyl/crispy-robot.git
2. cd crispy-robot, run `npm install`
3. `mkdir posts`, then copy all your posts which are `markdown` format to `posts` folder
4. open site.conf.json

```
{
"username": "your-github-username",
"repo": "your-github-repo",
"branch": "gh-pages"
}
```
  
5. run `npm run deploy`, that's it!

### TODO:
- [ ] theme support
- [ ] render html from template, so that page contents like `title` can be easily added
- [ ] a markdown editor is working in progress

Pull requests are welcome!