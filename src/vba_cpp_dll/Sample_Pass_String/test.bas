Declare Function upper_heap Lib "Sample.dll" (ByVal str$) As String
Declare Function upper_arg Lib "Sample.dll" (ByVal str$, ByVal out$, ByVal n As Long) As Long
Declare Function upper_bstr Lib "Sample.dll" (ByVal str$) As String
Declare Function upper_bstr_bstr Lib "Sample.dll" (ByVal str As String) As String
Declare Function upper_var Lib "Sample.dll" (ByVal str$) As Variant


Const s As String = "abcdlk"

Function upper_vba_arg(str)
    Dim n&, out$
    n = Len(str)
    out = Space(n)
    Call upper_arg(str, out, n)
    upper_vba_arg = out
End Function

Function upper_vba_bstr(str) As String
    upper_vba_bstr = upper_bstr(str)
End Function

Function upper_vba_bstr_bstr(str) As String
    upper_vba_bstr_bstr = upper_bstr_bstr(str)
End Function

Function upper_vba_var(str)
    upper_vba_var = StrConv(upper_var(str), vbUnicode)
End Function


Sub test1()
    Dim out$
    out = upper_heap(s)
    Debug.Print out
End Sub

Sub test2()
    Dim out$
    out = upper_vba_arg(s)
    Debug.Print out
End Sub

Sub test31()
    Dim out$
    out = upper_vba_bstr(s)
    Debug.Print out
End Sub

Sub test32()
    Dim out$
    out = upper_vba_bstr_bstr(s)
    Debug.Print out
End Sub

Sub test4()
    Dim out$
    out = upper_vba_var(s)
    Debug.Print out
End Sub

