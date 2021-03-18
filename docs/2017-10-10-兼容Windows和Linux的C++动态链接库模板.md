---
keywords: C++, 动态链接库
tags: [C++]
---

# 兼容Windows和Linux的C++动态链接库模板

2017-10-10

---

## 关键点

- Windows下可以使用`__declspec()`修饰类的导出和导入，使用`__stdcall`修饰导出函数

- Linux平台无需指定导入导出类时无需指定以上修饰名称

- 考虑到C++的`Name Mangling`，可以使用`extern "C" {...}`修饰需要导出的函数

## 模板

    // interface.h
    # ifndef INTERFACE_H
    # define INTERFACE_H
    # ifdef _WIN32
    #     ifdef INTERFACE_LIB
    #          define INTERFACE_EXPORT __declspec(dllexport)
    #     else
    #          define INTERFACE_EXPORT __declspec(dllimport)
    #     endif
    #     define INTERFACE_EXPORT_C __stdcall
    # endif

    # ifdef linux
    #     define INTERFACE_EXPORT
    #     define INTERFACE_EXPORT_C
    # endif

    // exported class
    class INTERFACE_EXPORT FOO{ ... };

    // exported functions
    extern "C" {
        void INTERFACE_EXPORT_C bar();
    }

    # endif
    ```

    ```
    // interface.cpp
    # define INTERFACE_LIB
    # include "interface.h"

    // exported class
    FOO::FOO() { ... }
    void FOO::foo() { ... }

    // exported functions
    void INTERFACE_EXPORT_C bar() { ... }