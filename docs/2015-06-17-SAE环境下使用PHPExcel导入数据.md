---
categories: [web development]
tags: [ThinkPHP, web]
---

# SAE环境下使用PHPExcel导入数据


---

当我们将一些涉及文件读写的项目移到云计算平台上，可能发现某些在本地运行得好好的功能会突然失效。例如，之前处理的是MySQL数据库备份还原功能在新浪云上的修改。本文将以ThinkPHP框架为例，处理SAE环境下使用PHPExcel插件导入数据的问题。

本地使用PHPExcel导入数据的流程为：先上传文件到服务器，然后将文件路径提供给PHPExcel以便读取文件，最后操作Excel文件的内容。关键代码如下：

``` php
Vendor('Classes.PHPExcel');    //将phpExcel插件放在vender文件夹下
// 1、上传文件到服务器
// ...
// 2、获取生成的文件路径
// $filetmpname = ...
// 3、读取和操作文件
$objPHPExcel = PHPExcel_IOFactory::load($filetmpname);
$arrExcel = $objPHPExcel->getSheet(0)->toArray();    // 单元格内容二维数组
// ...
```

这个流程在SAE环境下还是一样的，只不过Storage中的文件无法像本地文件那样直接被`PHPExcel_IOFactory::load()`所读取。因此，需要处理上面代码中的第二步，为PHPExcel提供一个可以读取的路径。经测试，下面三种方法都是可行的。

## 直接读取到TmpFS

SAE上不允许写本地文件，但是提供了常量`SAE_TMP_PATH`，可以往这个目录下写入临时文件。这里的临时文件有着特别的生命周期，当前页面的请求执行完以后，这个文件就会被删除。TMPFS的介绍和示例 [^1]。


TMPFS相当于把文件读取到内存中，对应_1上传文件到服务器_的步骤。第二步，获取文件路径可参考如下代码

``` php
// 设置一个临时路径
$filetmpname = SAE_TMP_PATH . "temp.xlsx";
// 将待上传的文件直接上传到上面的路径
file_put_contents($filetmpname,file_get_contents($_FILES['file']['tmp_name']));
// 读取和操作文件 ...
```

## 上传到Storage

如果希望在Storage中也保存一份导入数据的文件，那就使用下面的流程：上传到Storage→从Storage读取到内存→提供给PHPExcel操作。本质上，这也是使用了TmpFS功能。

``` php
// 1、上传文件到storage
if ($_FILES["file"]["error"] > 0){
    $this->ajaxReturn("",$_FILES["file"]["error"],0);
}
else{
    $domain = "public"; // storage名称，需要事先建立
    $filename_arr = explode(".",$_FILES["file"]["name"]);
    $filename_arr[0] = 'Uploads/' . date("ymdHis") . '_' . rand(10000, 99999);
    $filename = implode(".",$filename_arr);
    $tmp_name = $_FILES['file']['tmp_name'];
    $q = new SaeStorage();
    $result = $q->upload($domain, $filename, $tmp_name);
    if(!$result) {
        $this->ajaxReturn("","文件上传错误",0);
    }
}
// 2、从Storage读取到内存，获取生成的文件路径
$filetmpname = SAE_TMP_PATH . "temp.xlsx";
file_put_contents($filetmpname,$q->read($domain, $filename));
// 3、读取和操作文件
$objPHPExcel = PHPExcel_IOFactory::load($filetmpname);
$arrExcel = $objPHPExcel->getSheet(0)->toArray(); // 单元格内容二维数组
```

## 使用ThinkPHP的兼容SAE的文件上传类——UploadFile()

ThinkPHP的文件上传类已经兼容了本地和SAE的文件操作，因此上一节的方法也可以直接使用UploadFile类来实现。

``` php
// 兼容本地及SAE的环境的写法
// 1、上传文件：本地上传到指定的磁盘目录，SAE上传到指定的Storage目录
import('ORG.Net.UploadFile');        
$upload = new UploadFile();// 实例化上传类
$upload->maxSize = 3145728 ;// 设置附件上传大小为3M
$upload->allowExts = array('xlsx', 'xls');// 设置附件上传类型
$upload->savePath = './Public/Uploads/';// 设置附件上传目录
if(!$upload->upload()) {// 上传错误提示错误信息
    $this->ajaxReturn("",$upload->getErrorMsg(),0);
}
else{// 上传成功 获取上传文件信息
    $info =  $upload->getUploadFileInfo();            
}
// 2、获取生成的文件路径
if(defined('SAE_ACCESSKEY')){ // SAE环境
    $filename = $info[0][savepath].$info[0][savename];
    $filetmpname = SAE_TMP_PATH . "temp.xlsx";
    $q = new SaeStorage();
    file_put_contents($filetmpname,$q->read($domain, $filename));
}
else{  // 本地环境
    $filetmpname = $info[0][savepath].$info[0][savename];
}
// 3、读取和操作文件
$objPHPExcel = PHPExcel_IOFactory::load($filetmpname);
$arrExcel = $objPHPExcel->getSheet(0)->toArray(); // 单元格内容二维数组
```

[^1]: [Alpha2新功能之TMPFS](http://blog.sae.sina.com.cn/archives/53#more-53)