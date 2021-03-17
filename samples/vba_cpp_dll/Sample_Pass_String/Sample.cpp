#include "Sample.h"
#include <comdef.h>
#include <stdlib.h>

VARIANT Common::CheckExcelArray(VARIANT& ExcelArray)
{
	VARIANT dvout;
	switch (ExcelArray.vt)
	{
	case VT_DISPATCH:
		// if Array is a Range object expose its values through the IDispatch interface
	{
		EXCEPINFO excep;
		DISPPARAMS dispparams;
		unsigned int uiArgErr;
		DISPID dispidValue;
		LPOLESTR XName = LPOLESTR(L"Value");

		ExcelArray.pdispVal->GetIDsOfNames(IID_NULL, &XName,
			1, LOCALE_SYSTEM_DEFAULT, &dispidValue);

		dispparams.cArgs = 0;
		dispparams.cNamedArgs = 0;

		// Invoke PropertyGet and store values in dvout
		ExcelArray.pdispVal->Invoke(dispidValue, IID_NULL,
			LOCALE_SYSTEM_DEFAULT, DISPATCH_PROPERTYGET,
			&dispparams, &dvout, &excep, &uiArgErr);

		// Comment this line out for proper working under Excel 2007
		// Don't stil know why it is this way; trying to figure out

		//ExcelArray.pdispVal->Release();

		return dvout;
	}
	break;

	default:
		//if the Array is a VBA SAFEARRAY return it as such
		return ExcelArray;
		break;

	}

	VariantClear(&dvout);
	VariantClear(&ExcelArray);
}

char* Common::Wchar2char(const wchar_t* wchar)
{
	size_t len = wcslen(wchar) + 1;
	size_t converted = 0;
	char* str;
	str = (char*)malloc(len* sizeof(char));
	wcstombs_s(&converted, str, len, wchar, _TRUNCATE);

	return str;
}

wchar_t* Common::Char2wchar(const char* str)
{
	size_t len = strlen(str) + 1;
	size_t converted = 0;
	wchar_t* wchar;
	wchar = (wchar_t*)malloc(len* sizeof(wchar_t));
	mbstowcs_s(&converted, wchar, len, str, _TRUNCATE);

	return wchar;
}

char* EXPORT_C upper_heap(const char* str)
{
	char* res = new char[strlen(str)+1];
	size_t i = 0;
	for (; str[i]; i++) {
		res[i] = toupper(str[i]);
	}
	res[i] = '\0';

	return res; // res should be released out of this function
}

BSTR EXPORT_C upper_bstr_wchar(const wchar_t* wchar)
{
	char* str = Common::Wchar2char(wchar);
	char* res = upper_heap(str);
	wchar_t* wchar_res = Common::Char2wchar(res);

	BSTR bstr = SysAllocString(wchar_res);

	free(str);
	free(wchar_res);
	delete[] res;

	return bstr;
}

BSTR EXPORT_C upper_bstr_bstr(BSTR str)
{
	return upper_bstr_wchar(str);
}

BSTR EXPORT_C upper_bstr_var(VARIANT cell)
{
	// convert from CELL
	cell = Common::CheckExcelArray(cell);

	BSTR bstr = cell.vt == VT_BSTR ? cell.bstrVal : SysAllocString(L"");	
	return upper_bstr_bstr(bstr);
}
