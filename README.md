# 4d-plugin-process
Get and set process variables, read command line arguments

### Platform

| carbon | cocoa | win32 | win64 |
|:------:|:-----:|:---------:|:---------:|
|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|

### Version

<img src="https://cloud.githubusercontent.com/assets/1725068/18940649/21945000-8645-11e6-86ed-4a0f800e5a73.png" width="32" height="32" /> <img src="https://cloud.githubusercontent.com/assets/1725068/18940648/2192ddba-8645-11e6-864d-6d5692d55717.png" width="32" height="32" />

## Syntax

```
PROCESS GET ARGUMENTS (arguments)
```

Parameter|Type|Description
------------|------------|----
arguments|ARRAY TEXT|

```
PROCESS SET VARIABLE (name;value)
PROCESS GET VARIABLE (name;value)
```

Parameter|Type|Description
------------|------------|----
name|TEXT|Process variable name
value|TEXT|Process variable value

```
PROCESS GET LIST (names;paths;ids)
```

Parameter|Type|Description
------------|------------|----
names|ARRAY TEXT|
paths|ARRAY TEXT|
ids|ARRAY LONGINT|

```
id:=PROCESS Get id 
```

Parameter|Type|Description
------------|------------|----
id|LONGINT|

