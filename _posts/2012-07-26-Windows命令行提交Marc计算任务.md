---
layout: post
author: Train
description: "Windows命令行提交Marc计算任务的指令及可能遇到的问题"
keywords: "Marc, 命令行"
---

完成有限元建模后，可以直接在MENTAT中执行计算，也可以使用`run_marc`命令直接在命令行提交计算任务。

## 操作流程

1. `WINDOWS+R`调出命令行窗口，进入Marc输入文件如`example.dat`所在目录
2. 输入`run_marc -j example -b n` ，提交计算

第一次执行过程中可能出现以下错误提示：

```
'#for' 不是内部或外部命令，也不是可运行的程序或批处理文件。
'getarch.bat' 不是内部或外部命令，也不是可运行的程序或批处理文件。
error, program
\run_marc_read.exe
which reads the command line options does not exist.
```

**解决方案**[[^1]]：在`marc2010\tools`目录中找到`run_marc.bat`文件，将第三行

`for %%i in (%0) do set DIRSCRIPT=%%~dpi`

修改为

`for %%i in (run_marc.bat) do set DIRSCRIPT=%%~dp$PATH:i`

## 参数说明

`run_marc`命令的控制参数有：

```
run_marc -prog prog_name -jid job_name -rid rid_name -pid pid_name 

-sid sid_name -queue queue_name -user user_name -back back_value 

-ver verify_value -save save_value -vf view_name -def def_name 

-nprocd number_of_processors (for Single Input file runs, use -nps

number_of_processors) -nthread number_of_threads 

-dir directory_where_job_is_processed -itree message_passing_type 

-host hostfile (for running over the network) -pq queue_priority 

-at date_time -comp compatible_machines_on_network -cpu time_limit 

-nsolver number of processors (MUMPS) -ml memory_limit -mode i4 -mpi intel-mpi
```

> 一般只需指定几个常用参数即可，以上参数的详细说明参考Marc2010帮助文档：《Volume A: Theory and User Information》。

## 常用实例
> run_marc -jid e2x1

单处理器后台运行任务`e2x1.dat` ，要求`e2x1.dat`在当前目录下

> run_marc -jid e2x14 -user u2x14 -sav y -b no -nprocd 4

4处理器前台运行任务`e2x1.dat` ，并使用用户子程序`u2x14.f`，计算完成后在相应目录下创建可执行模块`u2x14.marc` 。

## 参考资料

[^1]: [1] [run_marc后出现getarch.bat不是内部或外部命令，如何解决？](http://iknow.baidu.com/question/256648092.html)