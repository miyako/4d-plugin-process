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

		case 4 :
			PROCESS_GET_LIST(pResult, pParams);
			break;
			
		case 5 :
			PROCESS_Get_id(pResult, pParams);
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

void PROCESS_Get_id(sLONG_PTR *pResult, PackagePtr pParams)
{
	C_LONGINT returnValue;
	
#if VERSIONMAC
	ProcessSerialNumber psn;
	pid_t pid = 0;
	
	if(GetCurrentProcess(&psn) == noErr)
		GetProcessPID(&psn, &pid);
	
	returnValue.setIntValue(pid);
#else
	returnValue.setIntValue((unsigned int)GetCurrentProcessId());
#endif
	
	returnValue.setReturn(pResult);
}

void PROCESS_GET_LIST(sLONG_PTR *pResult, PackagePtr pParams)
{
	ARRAY_TEXT Param1;
	ARRAY_TEXT Param2;
	ARRAY_LONGINT Param3;
	
	Param1.setSize(1);
	Param2.setSize(1);
	Param3.setSize(1);
	
#if VERSIONWIN
	using namespace std;
	
	HANDLE hProcessSnap = INVALID_HANDLE_VALUE;
	PROCESSENTRY32 pe32;
	
	HANDLE hModuleSnap = INVALID_HANDLE_VALUE;
	MODULEENTRY32 me32;
	
	hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
	
	if(hProcessSnap != INVALID_HANDLE_VALUE)
	{
		pe32.dwSize = sizeof(PROCESSENTRY32);
		
		if(Process32First(hProcessSnap, &pe32))
		{
			do
			{
				hModuleSnap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pe32.th32ProcessID);
				wstring process_name = pe32.szExeFile;
				if(hModuleSnap != INVALID_HANDLE_VALUE)
				{
					me32.dwSize = sizeof(MODULEENTRY32);
					
					if(Module32First(hModuleSnap, &me32))
					{
						do
						{
							wstring module_name = me32.szModule;
							
							if(module_name == process_name)
							{
								CUTF16String p1 = (const PA_Unichar*)me32.szModule;
								Param1.appendUTF16String(&p1);
								CUTF16String p2 = (const PA_Unichar*)me32.szExePath;
								Param2.appendUTF16String(&p2);
								Param3.appendIntValue(me32.th32ProcessID);
							}
							
						}while(Module32Next(hModuleSnap, &me32));
						CloseHandle(hModuleSnap);
					}
				}
				
			}while(Process32Next(hProcessSnap, &pe32));
			CloseHandle(hProcessSnap);
		}
	}
#else
	NSWorkspace *sharedWorkspace = [NSWorkspace sharedWorkspace];
	NSArray *launchedApplications = [sharedWorkspace launchedApplications];
	
	unsigned int i;
	
	for(i = 0; i < [launchedApplications count]; i++)
	{
		NSString *NSApplicationName = (NSString *)[[launchedApplications objectAtIndex:i] valueForKey:@"NSApplicationName"];
		Param1.appendUTF16String(NSApplicationName);
		
		NSString *NSApplicationPath = (NSString *)[[launchedApplications objectAtIndex:i] valueForKey:@"NSApplicationPath"];
		NSURL *url = [[NSURL alloc]initFileURLWithPath:NSApplicationPath];
		
		if(url)
		{
			NSString *filePath = (NSString *)CFURLCopyFileSystemPath((CFURLRef)url, kCFURLHFSPathStyle);
			Param2.appendUTF16String(filePath);
			[filePath release];
			[url release];
		}else{
			Param2.appendUTF16String(@"");
		}
		
		NSNumber *NSApplicationProcessIdentifier = (NSNumber *)[[launchedApplications objectAtIndex:i] valueForKey:@"NSApplicationProcessIdentifier"];
		Param3.appendIntValue([NSApplicationProcessIdentifier intValue]);
	}
#endif
	
	Param1.toParamAtIndex(pParams, 1);
	Param2.toParamAtIndex(pParams, 2);
	Param3.toParamAtIndex(pParams, 3);
	
}
