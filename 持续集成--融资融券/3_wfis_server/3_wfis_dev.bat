@echo off
ECHO 加载环境变量，请注意按需设置
set

set BUILD_ID=NOKILL


rem 获取工作路径
echo %mysvn_url%
set mysvn_url=%mysvn_url: =\%
for /f "tokens=*" %%i in ("%mysvn_url%.$") do set  last_path=%%~ni
set work_path=%WORKSPACE%\%last_path%

rem 如果lbmdll有代码变化才会生成目录lbmdll
cd /d %work_path%
findstr . 11.txt&&set exist=1||set exist=0
if %exist%==1 (
cd /d %work_path%\lbmdll

rem 把编译生成的lbmdll文件放到newlbmdll目录
if exist newlbmdll\lbm (
rd /Q /S newlbmdll\lbm
)

if not exist newlbmdll\lbm (
mkdir newlbmdll\lbm
)
for /f %%i in (..\3_dll.txt) do (xcopy bin\%%i.dll newlbmdll\lbm /s /d /y /h)

if not exist newlbmdll\bin (
mkdir newlbmdll\bin
)
for /f %%i in (..\4_bin.txt) do (xcopy bin\%%i newlbmdll\bin /s /d /y /h)

echo 挪一下特殊lbm的位置
pushd newlbmdll\lbm
if exist "lbm_fundtrans.dll" (
if not exist "plugins" mkdir plugins 
move /Y lbm_fundtrans.dll plugins
)

pushd newlbmdll\lbm
if exist "lbm_stktrans.dll" (
if not exist "plugins" mkdir plugins 
move /Y lbm_stktrans.dll plugins
)

if exist "lbm_zjxt_itf.dll" (
if not exist "plugins" mkdir plugins 
move /Y lbm_zjxt_itf.dll plugins
)
if exist "lbm_swhy.dll" (
if not exist "swhy" mkdir swhy 
move /Y lbm_swhy.dll swhy 
)
popd

echo 更新后台xml配置文件
if exist newbin\bin (
rd /Q /S newbin\bin
)

if not exist newbin\bin (
mkdir newbin\bin
cd.>newbin\bin\kcbpspd.xml
cd.>newbin\bin\kcbpspd_add.xml
)

xcopy /y bin\kcbpspd_优化版.xml newbin\bin\kcbpspd.xml

for /f "tokens=2 delims= " %%i in ('findstr /c:"kcbpspd" ..\11.txt') do (svn diff -x-w -r %Start_version%:%TO_VERSION% %%i>1.xml )
findstr /bc:"+"  1.xml|findstr /vc:"+++">2.xml
cd.>kcbpspd_add.xml
for /f "tokens=1 delims=+" %%i in (2.xml) do echo %%i>>kcbpspd_add.xml
move /y kcbpspd_add.xml newbin\bin\kcbpspd_add.xml

for /f "tokens=2 delims= " %%i in ('findstr /c:"DataTransfer.xml" ..\11.txt') do svn export %%i newbin\bin


echo 同步后台服务器

rem 清空升级包目录
if exist %PATCH_NAME%\KCBP (
rd /Q /S %PATCH_NAME%\KCBP
) 

rem 整理升级包目录
if not exist %PATCH_NAME%\KCBP (
mkdir %PATCH_NAME%\KCBP
)

xcopy %work_path%\lbmdll\newbin %PATCH_NAME%\KCBP /S /H /D /Y
xcopy %work_path%\lbmdll\newlbmdll %PATCH_NAME%\KCBP /S /H /D /Y
) else (
echo %work_path%\lbmdll不存在
exit 0
)
