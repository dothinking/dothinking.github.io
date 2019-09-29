#pragma once

#define EXPORT_C __stdcall

#include <OAIdl.h> // for VARIANT, BSTR etc


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
	int EXPORT_C upper_char(const char* str, char* out, int n_size);

	// return string directly with BSTR
	BSTR EXPORT_C upper_bstr(const char* str);

	// return string with Variant
	VARIANT EXPORT_C upper_var(const char* str);
}