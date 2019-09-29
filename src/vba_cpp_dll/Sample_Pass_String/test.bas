Declare Function upper_bstr_wchar Lib "Sample_Passing_String.dll" (ByVal str$) As String
Declare Function upper_bstr_bstr Lib "Sample_Passing_String.dll" (ByVal str As String) As String
Declare Function upper_bstr_var Lib "Sample_Passing_String.dll" (ByVal str As Variant) As String


Const s As String = "abcdlk"

Function upper_vba_bstr_wchar(str As String) As String
    upper_vba_bstr_wchar = StrConv(upper_bstr_wchar(StrConv(str, vbUnicode)), vbFromUnicode)
End Function

Function upper_vba_bstr_bstr(str As String) As String
    upper_vba_bstr_bstr = StrConv(upper_bstr_bstr(StrConv(str, vbUnicode)), vbFromUnicode)
End Function

Function upper_vba_bstr_var(str As String) As String
    upper_vba_bstr_var = StrConv(upper_bstr_var(str), vbFromUnicode)
End Function

Sub test_wchar()
    Dim out$
    out = upper_vba_bstr_wchar(s)
    Debug.Print out
End Sub

Sub test_bstr()
    Dim out$
    out = upper_vba_bstr_bstr(s)
    Debug.Print out
End Sub

Sub test_var()
    Dim out$
    out = upper_vba_bstr_var(s)
    Debug.Print out
End Sub
