#include "Sample.h"

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

int EXPORT_C upper_char(const char* str, char* out, int n_size)
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

	// convert to BSTR -> String type in VBA
	// SysAllocStringByteLen() gets an ANSI string, but _bstr_t() gets Unicode string
	// e.g. ANSI "ABC" to Unicode "A B C "
	// using StrConv(str, vbFromUnicode) in VBA for Unicode to ANSI conversion
	BSTR bstr = SysAllocStringByteLen(res, strlen(res));

	delete[] res;
	return bstr;
}

VARIANT EXPORT_C upper_var(const char* str)
{
	BSTR bstr = upper_bstr(str);
	VARIANT var;
	var.vt = VT_BSTR;
	var.bstrVal = bstr;
	return var;
	VariantClear(&var);
}