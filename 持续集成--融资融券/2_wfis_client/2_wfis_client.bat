@echo on
:加载环境变量
set

set BUILD_ID=NOKILL

echo 获取工作路径
set mysvn_url=%mysvn_url: =\%
for /f "tokens=*" %%i in ("%mysvn_url%.$") do set  last_path=%%~ni
set work_path=%WORKSPACE%\%last_path%
rem 如果11.txt有内容则往下走，否则最后结束
cd /d %work_path%
findstr . 11.txt&&set exist=1||set exist=0
echo %exist%

if %exist%==1 (
cd /d %work_path%\Client
rem 把编译生成的client的dll文件放到addbin目录
if not exist "addbin" (mkdir addbin\bin) else (del /q addbin\bin\*.*)
for /f %%i in (..\3_dll.txt) do xcopy bin\%%i.dll addbin\bin /s /d /y /h
echo 生成的client的dll文件已经复制到addbin目录
)
rem 如果代码没有更新则直接跳出
if %exist%==0 (
echo %work_path%\Client不存在
exit 0
)


rem 把report的更新的rpt文件放到addreport目录
if not exist "addreport" (mkdir addreport\report) else (del /q addreport\report\*.*)
cd.>..\4_rpt.txt
for /f "delims=" %%i in ('findstr /i "\/Client/Report/" ..\11.txt') do (
for /f "tokens=2 delims= " %%j in ("%%i") do @echo %%j>>..\4_rpt.txt
)
findstr . ..\4_rpt.txt&&set a=exist||set a=notexist
echo a=%a%
IF "%a%"=="exist" (
for /f "tokens=*" %%i in (..\4_rpt.txt) do svn export --force %%i
move /y *.rpt addreport\report
echo 本次前端有需要更新的report文件
) 
IF "%a%"=="notexist" (
set ERRORLEVEL=0
echo 本次前端没有需要更新的report文件
)


rem 把bin的更新的xml文件放到addbin目录
cd.>..\5_xml.txt
for /f "delims=" %%i in ('findstr /i /c:"rzrq2sztoes.xml" ..\11.txt') do (
for /f "tokens=2 delims= " %%j in ("%%i") do @echo %%j>>..\5_xml.txt
)
findstr . ..\5_xml.txt&&set b=exist||set b=notexist
echo b=%b%
IF "%b%"=="exist" (
for /f "tokens=*" %%i in (..\5_xml.txt) do svn export --force %%i
move /y rzrq2sztoes.xml addbin\bin
echo 本次前端有需要更新的xml文件
)
IF "%b%"=="notexist" (
set ERRORLEVEL=0
echo 本次前端没有需要更新的xml文件
)

rem add  更新的 exe 文件 拷贝到 addbin\bin目录 2019-01-25 09:05:02 王兵宗
cd.>..\6_exe.txt
findstr . 6_exe.txt&&set exist=1||set exist=0
echo %exist%
if %exist%==1 (
cd /d %work_path%\Client
echo 把编译生成的client的exe文件放到addbin目录
for /f %%i in (..\6_exe.txt) do xcopy bin\%%i addbin\bin /s /d /y /h
echo 生成的client的dll文件已经复制到addbin目录
)
rem 如果代码没有更新则直接跳出
if %exist%==0 (
echo %work_path%\Client不存在
exit 0
)

echo 同步至文件共享服务器

rem 清空升级包目录
if exist %PATCH_NAME%\spbclient (
rd /Q /S %PATCH_NAME%\spbclient
) 

rem 整理升级包目录
if not exist %PATCH_NAME%\spbclient (
mkdir %PATCH_NAME%\spbclient
)

if %exist%==1 (
xcopy %work_path%\Client\addbin %PATCH_NAME%\spbclient /S /H /D /Y
)

IF "%a%"=="exist" (
xcopy %work_path%\Client\addreport %PATCH_NAME%\spbclient /S /H /D /Y
)
echo 前端更新完成，请自取更新覆盖客户端文件。
