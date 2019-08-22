#include "Sample.h"
#include <comdef.h>

vector<vector<double>> Common::GetExcelRangeInput(VARIANT range)
{
	// check if Array is a Range object
	if (range.vt == VT_DISPATCH) range = CheckExcelArray(range);

	// get the number columns and rows
	long ncols, nrows;
	ncols = (range.parray)->rgsabound[0].cElements;
	nrows = (range.parray)->rgsabound[1].cElements;

	// convert to 2D vector
	vector<vector<double>> res(nrows, vector<double>(ncols));
	VARIANT var;
	for (long i = 0; i < nrows; i++)
	{
		for (long j = 0; j < ncols; j++)
		{
			long indi[] = { i + 1,j + 1 };
			// store in a VARIANT variable first
			SafeArrayGetElement(range.parray, indi, &var);
			res[i][j] = var.dblVal;
		}
	}

	return res;

	VariantClear(&range);
	VariantClear(&var);
}

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

int EXPORT_C upper_arg(const char* str, char* out, int n_size)
{
	char* res = upper_heap(str);
	size_t n = strlen(res) < n_size ? strlen(res) : n_size;
	strncpy(out, res, n); // for safe, the max buffer n_size is used
	delete[] res;
	return n;
}

BSTR EXPORT_C upper_bstr(const char* str)
{
	char* res = upper_heap(str);	
	BSTR bstr = SysAllocStringByteLen(res, strlen(res));
	delete[] res;
	return bstr;
}

BSTR EXPORT_C upper_bstr_bstr(BSTR str)
{
	char* char_str = (char*) str;
	return upper_bstr(char_str);
}

VARIANT EXPORT_C upper_var(const char* str)
{
	char* res = upper_heap(str);
	BSTR bstr = SysAllocStringByteLen(res, strlen(res));
	delete[] res;

	VARIANT var;
	var.vt = VT_BSTR;
	var.bstrVal = bstr;
	return var;
	VariantClear(&var);
}