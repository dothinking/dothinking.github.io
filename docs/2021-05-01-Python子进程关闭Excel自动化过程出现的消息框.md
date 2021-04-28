---
categories: [process automation]
tags: [python]
---

#  Python子进程关闭Excel自动化过程出现的消息框


---


利用Python实现Excel自动化，尤其是涉及VBA时，有可能好心出现消息框 [^1] [^2]，例如动作完成后的一个VBA弹窗（MsgBox）。此时需要人为响应，否则代码卡死直至超时。当然，根本的方法是VBA代码中不要出现类似弹窗；但有时我们无权修改被操作的Excel文件，例如这是我们进行自动化测试的对象。所以本文记录从代码角度解决此类问题的方法。

## 假想场景

使用`xlwings`（或者其他自动化库）打开Excel文件`test.xlsm`，读取`Sheet1!A1`单元格内容。很简单的一个操作：

    import xlwings as xw
    
    wb = xw.Book('test.xlsm')
    msg = wb.sheets('Sheet1').range('A1').value
    print(msg)
    wb.close()

然而不幸的是，这个文件在打开工作簿时进行了热情的欢迎仪式：

    Private Sub Workbook_Open()
        MsgBox "Welcome"
        MsgBox "to open"
        MsgBox "this file."
    End Sub

第一个弹窗`Welcome`就卡住了Excel，Python代码相应被卡死在第一行。


## 基本思路

主程序中不可能直接处理或者绕过此类问题，也不能奢望有人随时蹲守解决此类问题——那就新开一个线程来坚守吧。因此，解决方案是利用子线程监听并随时关闭弹窗，直到主程序圆满结束。

Excel弹窗默认的标题是`Microsoft Excel`，接下来以此为例捕捉窗口并点击按钮。


## pywinauto方案

`pywinauto`顾名思义是Windows界面自动化库，模拟鼠标和键盘操作窗体和控件 [^3]。不同于先获取句柄再获取属性的传统方式，`pywinauto`的API更加友好和pythonic。例如，两行代码就可以实现窗口捕捉和点击：

    win = Application(backend="win32").connect(title='Microsoft Excel')
    win.Dialog.Button.click()


自定义一个线程类执行以上操作：

    # listener_pywinauto.py
    import time
    from threading import Thread, Event
    from pywinauto.application import Application


    class MsgBoxListener(Thread):

        def __init__(self, title:str, interval:int):
            Thread.__init__(self)
            self._title = title 
            self._interval = interval 
            self._stop_event = Event()   

        def stop(self): self._stop_event.set()

        @property
        def is_running(self): return not self._stop_event.is_set()

        def run(self):
            while self.is_running:
                try:
                    time.sleep(self._interval)
                    self._close_msgbox()
                except Exception as e:
                    print(e, flush=True)


        def _close_msgbox(self):
            '''Close the default Excel MsgBox with title "Microsoft Excel".'''        
            win = Application(backend="win32").connect(title=self._title)
            win.Dialog.Button.click()


    if __name__=='__main__':
        t = MsgBoxListener('Microsoft Excel', 1)
        t.start()
        time.sleep(10)
        t.stop()


最终，在开始主要操作前启动子线程，并在结束后关闭：

    import xlwings as xw
    from listener_pywinauto import MsgBoxListener

    # start listen thread
    listener = MsgBoxListener('Microsoft Excel', 3)
    listener.start()

    # main process
    wb = xw.Book('test.xlsm')
    msg = wb.sheets('Sheet1').range('A1').value
    print(msg)
    wb.close()

    # stop listener thread
    listener.stop()


到此问题基本解决，本地运行效果完全达到预期。但我的真实需求是以系统服务方式在服务器上进行Excel文件自动化测试，后续发现，当以系统服务方式运行时，`pywinauto`竟然捕捉不到弹窗！这或许是`pywinauto`一个潜在的问题 [^4]。


## win32gui方案

那就只好转向相对底层的`win32gui`（实际是`pywin32`库的一部分），所幸解决了上述问题。

    # pip install pywin32
    import win32gui
    import win32con


以下仅列出`MsgBoxListener`类中关键操作，其余代码完全一致：

    def _close_msgbox(self):
        # find the top window by title
        hwnd = win32gui.FindWindow(None, self._title)
        if not hwnd: return

        # find child button
        h_btn = win32gui.FindWindowEx(hwnd, None,'Button', None)
        if not h_btn: return

        # show text
        text = win32gui.GetWindowText(h_btn)
        print(text)

        # click button        
        win32gui.PostMessage(h_btn, win32con.WM_LBUTTONDOWN, None, None)
        time.sleep(0.2)
        win32gui.PostMessage(h_btn, win32con.WM_LBUTTONUP, None, None)
        time.sleep(0.2)


再进一步，原VBA代码可能不是采用默认的弹窗标题，因此我们不能仅根据标题进行捕捉。那就扩大化范围，尝试点击任何包含确定性按钮（例如OK，Yes，Confirm）的窗口。

    def _close_msgbox(self):
        '''Click button to close message box if has text "OK", "Yes" or "Confirm".'''
        # Get handles of all top wondows
        h_windows = []
        win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), h_windows) 
        
        for h_window in h_windows:            
            # Get child button with text OK, Yes or Confirm of given window.
            h_btn = win32gui.FindWindowEx(h_window, None,'Button', None)
            if not h_btn: continue

            # check button text
            text = win32gui.GetWindowText(h_btn)
            if not text.lower() in ('ok', 'yes', 'confirm'): continue

            # click button
            win32gui.PostMessage(h_btn, win32con.WM_LBUTTONDOWN, None, None)
            time.sleep(0.2)
            win32gui.PostMessage(h_btn, win32con.WM_LBUTTONUP, None, None)
            time.sleep(0.2)




[^1]: [Handling VBA popup message boxes in Microsoft Excel](https://stackoverflow.com/questions/51817465/handling-vba-popup-message-boxes-in-microsoft-excel)
[^2]: [Trying to catch MsgBox text and press button in xlwings](https://stackoverflow.com/questions/56530310/trying-to-catch-msgbox-text-and-press-button-in-xlwings)
[^3]: [What is pywinauto](https://pywinauto.readthedocs.io/en/latest/)
[^4]: [Remote Execution Guide](https://pywinauto.readthedocs.io/en/latest/remote_execution.html)