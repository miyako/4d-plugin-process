# 4d-plugin-process
Get and set process variables, read command line arguments

![version](https://img.shields.io/badge/version-18%2B-EB8E5F)
![platform](https://img.shields.io/static/v1?label=platform&message=mac-intel%20|%20mac-arm%20|%20win-64&color=blue)
[![license](https://img.shields.io/github/license/miyako/4d-plugin-process)](LICENSE)
![downloads](https://img.shields.io/github/downloads/miyako/4d-plugin-process/total)

## Syntax

```4d
PROCESS GET ARGUMENTS(arguments)
```

Parameter|Type|Description
------------|------------|----
arguments|ARRAY TEXT|

```4d
PROCESS SET VARIABLE(name;name)
PROCESS GET VARIABLE(name;value)
```

Parameter|Type|Description
------------|------------|----
name|TEXT|
value|TEXT|

```4d
PROCESS GET LIST(name;path;pid)
```

Parameter|Type|Description
------------|------------|----
name|ARRAY TEXT|
path|ARRAY TEXT|
pid|ARRAY LONGINT|

```4d
pid:=PROCESS Get id 
```

Parameter|Type|Description
------------|------------|----
pid|LONGINT|
