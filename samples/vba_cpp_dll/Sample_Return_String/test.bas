Declare Function upper_heap Lib "Sample_Return_String.dll" (ByVal str$) As String
Declare Function upper_char Lib "Sample_Return_String.dll" (ByVal str$, ByVal out$, ByVal n As Long) As Long
Declare Function upper_bstr Lib "Sample_Return_String.dll" (ByVal str$) As String
Declare Function upper_var Lib "Sample_Return_String.dll" (ByVal str$) As Variant


Const s As String = "abcdlk"

Function upper_vba_char(str)
    Dim n&, out$
    n = Len(str)
    out = Space(n)
    Call upper_char(str, out, n)
    upper_vba_char = out
End Function

Function upper_vba_bstr(str) As String
    upper_vba_bstr = upper_bstr(str)
End Function

Function upper_vba_var(str)
    upper_vba_var = StrConv(upper_var(str), vbUnicode)
End Function


Sub test_heap()
    Dim out$
    out = upper_heap(s)
    Debug.Print out
End Sub

Sub test_char()
    Dim out$
    out = upper_vba_char(s)
    Debug.Print out
End Sub

Sub test_bstr()
    Dim out$
    out = upper_vba_bstr(s)
    Debug.Print out
End Sub

Sub test_var()
    Dim out$
    out = upper_vba_var(s)
    Debug.Print out
End Sub


