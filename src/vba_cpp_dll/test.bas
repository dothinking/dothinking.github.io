Declare Function upper_heap Lib "D:\07_GitHub\blog\src\vba_cpp_dll\Release\Sample.dll" (ByVal str$) As String
Declare Function upper_arg Lib "D:\07_GitHub\blog\src\vba_cpp_dll\Release\Sample.dll" (ByVal str$, ByVal out$, ByVal n As Long) As Long
Declare Function upper_bstr Lib "D:\07_GitHub\blog\src\vba_cpp_dll\Release\Sample.dll" (ByVal str$) As String
Declare Function upper_bstr_bstr Lib "D:\07_GitHub\blog\src\vba_cpp_dll\Release\Sample.dll" (ByVal str$) As String
Declare Function upper_var Lib "D:\07_GitHub\blog\src\vba_cpp_dll\Release\Sample.dll" (ByVal str$) As Variant


Const s = "12aBcDe"
Public out As String


Sub test1()
    out = upper_heap(s)
    Debug.Print out
End Sub

Sub test2()
    Dim n&
    n = Len(s)
    out = Space(n)
    Call upper_arg(s, out, n)
    Debug.Print out
End Sub


Sub test3()
    out = upper_bstr(s)
    Debug.Print out
    
    out = upper_bstr_bstr(s)
    Debug.Print out
End Sub

Sub test4()
    out = upper_var(s)
    Debug.Print out
End Sub



Function upper_vba_arg(str)
    Dim n&, out$
    n = Len(str)
    out = Space(n)
    Call upper_arg(str, out, n)
    upper_vba_arg = out
End Function

Function upper_vba_bstr(str)
    upper_vba_bstr = upper_bstr(str)
End Function

Function upper_vba_var(str As Range) As String
    upper_vba_var = upper_var(str.Value)
End Function
