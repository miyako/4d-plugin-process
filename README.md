# 4d-plugin-process
Get and set process variables, read command line arguments

Previous (v16 or earlier) available in [thread-unsafe](https://github.com/miyako/4d-plugin-process/tree/thread-unsafe) branch

![version](https://img.shields.io/badge/version-18%2B-EB8E5F)
![platform](https://img.shields.io/static/v1?label=platform&message=mac-intel%20|%20mac-arm%20|%20win-64&color=blue)
[![license](https://img.shields.io/github/license/miyako/4d-plugin-process)](LICENSE)
![downloads](https://img.shields.io/github/downloads/miyako/4d-plugin-process/total)

## Syntax

```4d
arguments:=PROCESS Get arguments
```

Parameter|Type|Description
------------|------------|----
arguments|TEXT|``json``

```4d
PROCESS SET VARIABLES (dict)
dict:=PROCESS Get variables
```

Parameter|Type|Description
------------|------------|----
dict|TEXT|``json``

```4d
list:=PROCESS Get list
```

Parameter|Type|Description
------------|------------|----
list|TEXT|``json``

```4d
id:=PROCESS Get id 
```

Parameter|Type|Description
------------|------------|----
id|LONGINT|
