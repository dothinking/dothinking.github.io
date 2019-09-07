#pragma once

#define EXPORT_C __stdcall


#include <vector>
#include <OAIdl.h> // for VARIANT, BSTR etc

using namespace std;

namespace Common
{
	//---------------------------------------------------------------------------------------------
	// Passing Excel Range object to C++ arguement
	// https://www.codeproject.com/Articles/17733/A-C-DLL-for-Excel-that-uses-Arrays-and-Ranges
	//---------------------------------------------------------------------------------------------
	// This function takes the Array from Excel, a Range object or a VBA SAFEARRAY, 
	// and returns a VARIANT SAFEARRAY. 
	// (a) Range object: e.g. A1:B5
	// (b) VBA 2D array with index starts from 1, e.g.
	//
	// Dim Y(5, 1) As Variant
	// For i = 1 To 5
	//     Y(i, 1) = i
	// Next i
	//
	VARIANT CheckExcelArray(VARIANT& ExcelArray);

	// Convert an Excel Range (e.g. A1:B5), into 2D (e.g. 5x2) vector
	vector<vector<double>> GetExcelRangeInput(VARIANT range);

	// wchar_t* to char*
	char* Wchar2char(const wchar_t* wchar);
	wchar_t* Char2wchar(const char* str);
}


//------------------------------------------------------------------------------
// EXPORT C-STYLE FUNCTION FOR VBA
//------------------------------------------------------------------------------
extern "C"
{
	// TEST CASE 1: Pass and return string variables between C++ DLL and VBA

	// return a char* var created in heap (bad pratice), 
	// VBA can get a correct result but crush then
	char* EXPORT_C upper_heap(const char* str);

	// pass back return value with arguement, the return value is real length
	// of the result string, while the input n_size is a max buffer size
	int EXPORT_C upper_arg(const char* str, char* out, int n_size);

	// return string directly with BSTR
	BSTR EXPORT_C upper_bstr(const wchar_t* str);
	BSTR EXPORT_C upper_bstr_bstr(BSTR str);
	BSTR EXPORT_C upper_bstr_var(VARIANT cell);

	// return string with Variant
	VARIANT EXPORT_C upper_var(const wchar_t* str);
}