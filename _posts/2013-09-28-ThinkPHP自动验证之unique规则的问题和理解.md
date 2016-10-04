---
layout: post
author: Train
description: "ThinkPHP自动验证之unique规则说明"
keywords: "ThinkPHP, unique, 自动验证"
---

本文针对ThinkPHP自动验证部分学习过程中遇到的几个问题，经过查阅文档及思考理解，作了以下几个方面的总结记录：

> 1. 自动验证的实施
> 2. unique验证规则的问题
> 3. 验证信息的Ajax返回

## 自动验证的实施

自动验证是通过对表单提交的数据（可以是对应数据库表中的某些字段，也可以不是表中字段）设定一些验证规则，在`create()`操作时会根据此规则进行验证并给出相应信息，当然也可以进行手动验证。它包含两种方式：

* 静态方式：在模型类里面通过$_validate属性定义验证规则。
* 动态方式：使用模型类的validate方法动态创建自动验证规则。

```php
array(
array(验证字段1,验证规则,错误提示,[验证条件,附加规则,验证时间]),
array(验证字段2,验证规则,错误提示,[验证条件,附加规则,验证时间]),
....);
```

详见官方帮助手册
> [6.15 自动验证](http://doc.thinkphp.cn/manual/auto_validate.html)  
> [ThinkPHP3.1快速入门（12）自动验证](http://www.thinkphp.cn/info/171.html)

## unique自动验证规则的问题

根据第一部分的学习，已经可以建立如下规则：

```php
array('username',' ','用户名已经存在！',0,'unique',1)
```

该规则表示在插入数据时，需要验证username是否唯一。然而在学习初期可能遇到的问题是：

* 修改信息的时候，提示用户名已经存在。
* 插入信息时，username明明没有重复而提示用户名已经存在。

第一个问题，显然是验证时机的混淆。我们根据上下文很容易判断需要进行的是编辑更新操作，可是程序如何判断？

程序是根据**主键值是否存在**来判定所要进行的操作的。例如，对于插入操作来说，主键值显然不存在；而编辑操作时，主键已经在之前的插入操作中存在了。所以解决问题1的关键在于让程序知道目前操作是插入还是编辑。方法有两个：

* 基本方法：根据以上基本原理，编辑操作时，在表单的隐藏域中给出待编辑的记录的主键值，这样程序通过搜索数据库就可以知道这条记录已经存在，即是编辑操作。
* 直接方法：在调用`create()`函数时明确指明验证时机：`create($data,2)`。

第二个问题，根源在于此时恰好将username设为主键了。解决方法很简单，重新设计主键即可，例如一个自动增长的id。其实这个在ThinkPHP文档中也有一点说明：

> ThinkPHP的默认约定每个数据表的主键名采用统一的id作为标识，并且是自动增长类型的。系统会自动识别当前操作的数据表的字段信息和主键名称，所以即使你的主键不是id，也无需进行额外的设置，系统会自动识别[[^1]]。

事实上，假如没有设置一个与数据表内容可能没有直接关系的id作为主键，而是其他的更有意义的主键，例如这里的username的话，那么在对username的插入操作时就会出现问题2——username明明是唯一的却提示重复了。

更进一步，引起这一切的根源在于unique验证规则本身的设计，参照ThinkPHP开发包`Core`文件夹下`Model.class.php`文件关于`unique`的代码：

```php
case 'unique': // 验证某个值是否唯一
    if(is_string($val[0]) && strpos($val[0],','))
        $val[0]  =  explode(',',$val[0]);
    $map = array();
    if(is_array($val[0])) {
        // 支持多个字段验证
        foreach ($val[0] as $field)
            $map[$field]   =  $data[$field];
    }else{
        $map[$val[0]] = $data[$val[0]];
    }
    if(!empty($data[$this->getPk()])) { // 完善编辑的时候验证唯一
        $map[$this->getPk()] = array('neq',$data[$this->getPk()]);
    }
    if($this->where($map)->find())   return false;
    return true;
```

从这里可以看出unique的逻辑是，查找数据库中有没有与验证数据重复的记录，查询条件有两个并且是`and`的关系：

* 规则给出的字段、表单提交的数据，`$map[$val[0]] = $data[$val[0]]`
* 主键若存在，则要求表单提交的字段值与主键不相等，`$map[$this->getPk()] = array('neq',$data[$this->getPk()])`

这样就可以理解上面两个问题了：

* 问题1的第一个解决方法的道理在于，表单隐藏域中给出了主键值，则查询条件2保证了不会有重复记录。
* 对于问题2，若要插入的username恰好是主键，则查询条件2覆盖了条件1，而此时的条件是表单提交的主键值在数据库中不存在，这显然是满足的，所以提示重复了。

## 验证信息的Ajax返回

自动验证结合Ajax返回可以无刷新给出相关信息，ThinkPHP提供了`ajaxReturn()`函数[[^2]]

```php
$this->ajaxReturn(返回数据,提示信息,操作状态)
```

下面通过`create()`函数自动验证并将`getError()`得到错误信息通过`ajaxReturn()`返回。错误信息为数组形式，键为验证字段，值为相应的验证信息。

```php
if (!$m->create()){ // 如果创建失败 表示验证没有通过 输出错误提示信息
    $this->ajaxReturn('',$m->getError(),0);
}
```

前端Ajax请求及获取数据的Jquery代码：

```javascript
$(document).ready(function(){
    $("input[type='button']").click(function(){
        $.post("adduser",$('form').serialize(),function(data){  // $('form').serialize()提交表单数据
            var json = eval('('+data+')'); // 得到Json对象
            // 输入不合法
            if(json.status == 0){ // to do
            }
            // 写入数据库错误
            else if(json.status == 1){ // to do
            }
            // 成功新建
            else if(json.status == 2){ // to do
            }
        });
    });
})
```

## 参考资料

[^1]: [1] [ThinkPHP完全开发手册-6.4-数据主键](http://doc.thinkphp.cn/manual/primary_key.html)
[^2]: [2] [ThinkPHP完全开发手册-5.19-AJAX返回](http://doc.thinkphp.cn/manual/ajax_return.html)