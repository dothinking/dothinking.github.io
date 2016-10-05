---
layout: post
author: Train
description: "修改MySQLReback类使其适用于SAE的读写环境"
keywords: "MySQL, SAE, ThinkPHP, 备份还原"
---

之前一篇文章介绍了ThinkPHP框架下的MySQL数据库备份还原类的使用，后来将项目迁移到了新浪云计算平台上，由于无法像本地一样读写文件，备份、还原功能也就失效了。本文即针对此问题，对原来的`MySQLReback.class.php`文件作相应修改，以适应SAE环境。

## 思路

SAE不支持本地文件的读写，但是为我们提供了`Storage`用于数据的存储：

> Storage是SAE为开发者提供的分布式对象存储服务，旨在利用SAE在分布式以及网络技术方面的优势为开发者提供安全、简单、高效的存储服务。Storage支持文本、多媒体、二进制等任何类型的数据的存储。
 
因此，修改思路为：将原来的本地文件操作代码修改为兼容`SAE Storage`的文件读写操作。当然，关于Storage的开发文档是必不可少的：

> [Class SaeStorage](http://apidoc.sinaapp.com/class-SaeStorage.html)

## 读取备份目录下已有的文件

在项目的`Storage`菜单下新建一个名称为`public`的`domain`，将备份文件放在此`domain`下的`Backup`文件夹下。要实现读取这些文件，可以使用SAE提供的`getListByPath()`方法。该方法执行成功后返回包含文件信息（名称、大小、上传时间等）的数组（数组的具体形式由最后一个输入参数指定），执行失败后返回`false`。参数说明、示例、实现代码参考上面提供的开发文档。下面给出读取备份目录下的文件代码：

```php
public function getBacoverFiles(){        
    // 本地写法
    // ....
 
    // SAE上写法
    $domain = "public";
    $s = new SaeStorage();
    $files = $s->getListByPath($domain,"Backup",100);
    foreach($files["files"] as $k => $v){
        $list[$k]['FileName'] = $v["Name"];
        $list[$k]['FileTime'] = date("Y-m-d H:i:s",$v["uploadTime"]);
        $FileSize = $v["length"]/1024;
        if ($FileSize < 1024){
            $list[$k]['FileSize'] = number_format($FileSize,2).' KB';
        }
        else {
            $list[$k]['FileSize'] = number_format($FileSize/1024,2).' MB';
        }
    }
    $result["total"] = count($list);
    $result["rows"] = $list==null?array():$list;
    echo json_encode($list);
}
```

## 备份数据库

浏览一下`MySQLReback`类的实现代码，可以发现该类先生成备份文件的内容，然后写入到目标文件夹。因此为了兼容SAE环境，只需要修改保存文件的`setFile()`私有方法。对应这部分修改，SAE提供了`write()`方法供写入文件到Storage。由于`write()`方法第一个参数为domain的名称，所以为`MySQLReback`类的配置参数提供一个`domain`键值对：

```php
$domain = "public";
$config = array(
    'host' => C('DB_HOST'),
    'port' => C('DB_PORT'),
    'userName' => C('DB_USER'),
    'userPassword' => C('DB_PWD'),
    'dbprefix' => C('DB_PREFIX'),
    'charset' => 'UTF8',
    'domain' => $domain,
    'path' => $DataDir,
    'isCompress' => 0, //是否开启gzip压缩
    'isDownload' => 0  
);
```

通过是否定义一些SAE常量来判断是SAE还是本地开发环境，从而使用相应的文件操作代码

```php
private function setFile() {
    $recognize = '';
    $recognize = implode('_', $this->dbName);
    $fileName = $this->trimPath($this->config['path'] . self::DIR_SEP . $recognize.'_'.date('YmdHis') . '_' . mt_rand(100000000,999999999) .'.sql');        
    if(defined('SAE_ACCESSKEY')){// SAE环境
        $s = new SaeStorage();
        $result = $s->write($this->config['domain'], $fileName, $this->content);
        if (!$result) {
            $this->throwException('写入文件失败!');
        }
    }
    else{  
        // 本地 ...    
    }            
    if ($this->config['isDownload']) {
        $this->downloadFile($fileName);
    }
}
```

## 还原数据库

同理，还原数据库时只要修正读取还原文件的代码即可

```php
private function getFile($fileName) {
    $this->content = '';
    $fileName = $this->trimPath($this->config['path'] . self::DIR_SEP .$fileName);
    if(defined('SAE_ACCESSKEY')){// SAE环境
        $s = new SaeStorage();
        $this->content = $s->read($this->config['domain'], $fileName);
    }
    else{
        // 本地 ...
    }            
}
```

## 下载备份文件

```php
public function downloadFile($fileName) {
    ob_end_clean();
    header ("Cache-Control: must-revalidate, post-check=0, pre-check=0");
    header('Content-Description: File Transfer');
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename=' . basename($fileName));
    if(defined('SAE_ACCESSKEY')){// SAE环境
        $s = new SaeStorage();
        echo $s->read($this->config['domain'], $fileName);
    }
    else {
        readfile($fileName);
    }
    exit();
}
```
