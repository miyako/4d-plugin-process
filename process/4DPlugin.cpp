/* --------------------------------------------------------------------------------
 #
 #	4DPlugin.cpp
 #	source generated by 4D Plugin Wizard
 #	Project : Process
 #	author : miyako
 #	2016/07/20
 #
 # --------------------------------------------------------------------------------*/


#include "4DPluginAPI.h"
#include "4DPlugin.h"

void PluginMain(PA_long32 selector, PA_PluginParameters params)
{
	try
	{
		PA_long32 pProcNum = selector;
		sLONG_PTR *pResult = (sLONG_PTR *)params->fResult;
		PackagePtr pParams = (PackagePtr)params->fParameters;

		CommandDispatcher(pProcNum, pResult, pParams); 
	}
	catch(...)
	{

	}
}

void CommandDispatcher (PA_long32 pProcNum, sLONG_PTR *pResult, PackagePtr pParams)
{
	switch(pProcNum)
	{
// --- Process

		case 1 :
			PROCESS_GET_ARGUMENTS(pResult, pParams);
			break;

		case 2 :
			PROCESS_SET_VARIABLE(pResult, pParams);
			break;

		case 3 :
			PROCESS_GET_VARIABLE(pResult, pParams);
			break;

	}
}

// ------------------------------------ Process -----------------------------------


void PROCESS_GET_ARGUMENTS(sLONG_PTR *pResult, PackagePtr pParams)
{
	ARRAY_TEXT Param1;

#if VERSIONWIN
	int nArgs;
	LPWSTR *szArglist = CommandLineToArgvW(GetCommandLineW(), &nArgs);
	
	if(szArglist)
	{
		Param1.setSize(1);
		
		for(unsigned int i = 0; i < nArgs; ++i)
		{
			Param1.appendUTF16String((const PA_Unichar *)szArglist[i]);
		}
		LocalFree(szArglist);
	}
#else
	NSArray *arguments = [[NSProcessInfo processInfo]arguments];
	
	Param1.setSize(1);
	
	for(unsigned int i = 0;i < [arguments count];++i)
	{
		Param1.appendUTF16String([arguments objectAtIndex:i]);
	}
#endif

	Param1.toParamAtIndex(pParams, 1);
}

void PROCESS_SET_VARIABLE(sLONG_PTR *pResult, PackagePtr pParams)
{
	C_TEXT Param1;
	C_TEXT Param2;

	Param1.fromParamAtIndex(pParams, 1);
	Param2.fromParamAtIndex(pParams, 2);

#if VERSIONMAC
	CUTF8String name, value;
	Param1.copyUTF8String(&name);
	Param2.copyUTF8String(&value);
	
	if(name.length())
	{
		setenv((const char *)name.c_str(), (const char *)value.c_str(), 1);
	}
#else
	CUTF16String name, value;
	Param1.copyUTF16String(&name);
	Param2.copyUTF16String(&value);
	
	if(name.length())
	{
		SetEnvironmentVariable((LPCTSTR)name.c_str(), (LPCTSTR)value.c_str());
	}
#endif
}

void PROCESS_GET_VARIABLE(sLONG_PTR *pResult, PackagePtr pParams)
{
	C_TEXT Param1;
	C_TEXT Param2;

	Param1.fromParamAtIndex(pParams, 1);

#if VERSIONMAC
	CUTF8String name, value;
	Param1.copyUTF8String(&name);
	
	if(name.length())
	{
		value = CUTF8String((const uint8_t *)getenv((const char *)name.c_str()));
		Param2.setUTF8String(&value);
	}
#else
	DWORD size = 0;
	CUTF16String name, value;
	Param1.copyUTF16String(&name);
	
	if(name.length())
	{
		if(size = GetEnvironmentVariable((LPCTSTR)name.c_str(), NULL, 0))
		{
			std::vector<wchar_t> buf(size);
			GetEnvironmentVariable((LPCTSTR)name.c_str(), (LPTSTR)&buf[0], size);
			value = CUTF16String((const PA_Unichar *)&buf[0]);
			Param2.setUTF16String(&value);
		}
	}
#endif

	Param2.toParamAtIndex(pParams, 2);
}
