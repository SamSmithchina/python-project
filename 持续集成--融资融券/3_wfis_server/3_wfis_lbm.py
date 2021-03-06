﻿# -*- coding:utf-8 -*-

import pysvn, os, re, shutil, sys, socket

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
print "slaver host = " + str(ip)
print "sys.version = " + str(sys.version)
print "sys.defaultencoding = " + str(sys.getdefaultencoding())

# 引用参数begin
# 读取和设置环境变量:os.getenv() 与os.putenv()
PATCH_NAME = os.getenv("PATCH_NAME")
mysvn_url = os.getenv("mysvn_url")
Start_version = os.getenv("Start_version")
TO_VERSION = os.getenv("TO_VERSION")
Client_version = os.getenv("Client_version")
Lbmdll_version = os.getenv("Lbmdll_version")
Sql_version = os.getenv("Sql_version")
workspace = os.getenv("workspace")
SVN_REVISION = os.getenv("SVN_REVISION")
first = os.getenv("first")
# 引用参数end

print "PATCH_NAME     " + PATCH_NAME
print "mysvn_url      " + mysvn_url
print "Start_version  " + str(Start_version)
print "TO_VERSION     " + str(TO_VERSION)
print "Client_version " + str(Client_version)
print "Lbmdll_version " + Lbmdll_version
print "Sql_version    " + Sql_version
print "workspace      " + workspace
print "SVN_REVISION   " + str(SVN_REVISION)

# 声明全局变量pysvn.Revision,begin
revision_start = pysvn.Revision(pysvn.opt_revision_kind.number, int(Start_version))
revision_start1 = pysvn.Revision(pysvn.opt_revision_kind.number, int(Start_version) + 1)
revision_end = pysvn.Revision(pysvn.opt_revision_kind.head)
peg_revision = pysvn.Revision(pysvn.opt_revision_kind.unspecified)

print  "revision_start" + str(revision_start)
print  "revision_end" + str(revision_end)
print "peg_revision" + str(peg_revision)
# 声明全局变量pysvn.Revision,end

# 获取版本，生成工作目录begin
last_path = os.path.basename(mysvn_url)
work_path = workspace + "\\" + last_path
if os.path.exists(work_path):
    print("\n\n工作目录 " + work_path)
else:
    os.makedirs(work_path)
    # 获取版本，生成工作目录end
    print("\n\n获取版本，生成工作目录" + work_path)

os.chdir(work_path)  # 切换到工作目录work_path下工作
os.system("svn diff --summarize -r %Start_version%:%TO_VERSION% %mysvn_url%/lbmdll>11.txt")
s = open('11.txt', 'r+').read()  # 读取文件1.txt
num1 = len(s)  # 计算文件1.txt字长
print("打印文件字长的值" + str(num1))  # 打印文件字长的值
if num1 == 0:
    print("数据库没有代码更新，先把代码checkout到本地")  # 文件1.txt如果为空,数据库没有代码更新
    p = pysvn.Client()
    p.checkout(mysvn_url + "/lbmdll", work_path + "\\lbmdll")
    # 编译配置
    print ("编译第一步修改版本号完成 begin")
    os.chdir(work_path + "\\lbmdll")
    a = open("build.pl", 'r')
    c = open("build1.pl", 'w+')
    for i in a.readlines():
        if "our $g_Version " in i:
            b = i.replace(i, "our $g_Version = " + '"' + Lbmdll_version + '"' + ';')
            c.write(b + "\n")
        elif "our $g_Version_s " in i:
            s_verion = Lbmdll_version.replace('.', ',')
            v = i.replace(i, "our $g_Version_s = " + '"' + s_verion + '"' + ';')
            c.write(v + "\n")
        else:
            c.write(i)
    c.close()
    a.close()
    os.remove("build.pl")
    os.rename("build1.pl", "build.pl")
    print ("编译第一步修改版本号完成 end")
    os.chdir(work_path)
    os.system("svn diff --summarize -r %Start_version%:%TO_VERSION% lbmdll>1.txt")
    a = open("1.txt", "r")
    b = open("2.txt", "w")
    lbmdlldlllist = []
    for i in a.readlines():
        if "lbmdll\\lbm_" in i:
            c = i.split("\\")[1]
            print c
            b.write(c + "\n")
    b.close()
    a.close()
    a = open("2.txt", "rb")
    for i in a.readlines():
        if i in lbmdlldlllist:
            print i
        else:
            lbmdlldlllist.append(i)
    print lbmdlldlllist
    a = open("3_dll.txt", "wb")
    for i in lbmdlldlllist:
        a.write(i)
    a.close()
    os.chdir(work_path + "\\lbmdll")
    print (work_path + "\\lbmdll")
    print "first = " + first
else:
    print("数据库代码有更新")  # 文件1.txt如果不为空,数据库代码有更新

    # 更新源码,先把lbmdll目录check out到本地begin

    os.chdir(work_path)  # 切换到工作目录下工作
    if os.path.exists("version.txt"):
        print("version.txt已经存在")
        s = open('version.txt', 'w+')
        s.write(Start_version)
        s.close()
        p = pysvn.Client()
        p.cleanup(work_path + "\\lbmdll")
        # p.revert(work_path+"\\lbmdll",recurse=True)#解决工程文件被修改后冲突问题
        p.update(work_path + "\\lbmdll", revision_end)  # 更新代码svn update.
    else:
        p = pysvn.Client()
        p.checkout(mysvn_url + "/lbmdll", work_path + "\\lbmdll")
        s = open('version.txt', 'w+')
        s.write(Start_version)
        s.close()

    # 更新源码,先把 lbmdll目录check out到本地end
    print ("更新源码,先把lbmdll目录check out到本地end")

    # 编译配置
    print ("编译第一步修改版本号完成 begin")
    os.chdir(work_path + "\\lbmdll")
    a = open("build.pl", 'r')
    c = open("build1.pl", 'w+')
    for i in a.readlines():
        if "our $g_Version " in i:
            b = i.replace(i, "our $g_Version = " + '"' + Lbmdll_version + '"' + ';')
            c.write(b + "\n")
        elif "our $g_Version_s " in i:
            s_verion = Lbmdll_version.replace('.', ',')
            v = i.replace(i, "our $g_Version_s = " + '"' + s_verion + '"' + ';')
            c.write(v + "\n")
        else:
            c.write(i)
    c.close()
    a.close()
    os.remove("build.pl")
    os.rename("build1.pl", "build.pl")
    print ("编译第一步修改版本号完成 end")
    os.chdir(work_path)
    os.system("svn diff --summarize -r %Start_version%:%TO_VERSION% lbmdll>1.txt")
    a = open("1.txt", "rb")
    b = open("2.txt", "wb")
    lbmdlldlllist = []
    for i in a.readlines():
        if "lbmdll\\lbm_" in i:
            c = i.split("\\")[1]
            # print c
            b.write(c + "\n")
        if "plugins\\lbm_" in i:
            c = i.split("\\")[2]
            # print c
            b.write(c + "\n")
    b.close()
    a.close()
    a = open("2.txt", "rb")
    for i in a.readlines():
        if i in lbmdlldlllist:
            print i
        else:
            lbmdlldlllist.append(i)
    print lbmdlldlllist
    a.close()

    # 2019-01-22 09:32:10
    # 处理JRA的lbm_dll结束 begin
    # 读取 svn log ，记录在svnlog.txt中
    if not os.path.exists(work_path + "\\curl_result"):
        os.mkdir(work_path + "\\curl_result")
    JRA_Requirement = []
    log_list = p.log(mysvn_url, revision_start, revision_end, discover_changed_paths=True)
    svn_log_txt = open("svnlog.txt", "wb")
    os.system("del curl_result\* /Q")  # 清空 curl_result文件夹，清除之前的JRA页面
    for log in log_list:
        svn_log = "[ " + str(log.revision.number) + " ] "
        svn_log += log.message
        svn_log += "\n"
        svn_log_txt.writelines(svn_log)
        # svn  的日志格式 为： ZQWFDJD-13, wangyx:edit, 节点数据回传BPcallBP公共类
        # 通过[，,]号分割这个字符串
        log_split = log.message.split(',', 1)
        jra = log_split[0]
        if len(jra) > 12:  # 超出12位就考虑开发提交svn时写的日志不规范
            # 2019-01-22 16:54:09
            # 上面的中文逗号编码[\xef\xbc\x8c] ,还得切换编码格式UTF_8，
            log_split_2 = jra.split('\xef\xbc\x8c', 1)
            jra = log_split_2[0]
            if len(jra) > 12:
                log_split_3 = jra.split('，', 1)  # 刚发现有人用中文逗号[，]书写日志，
                jra = log_split_3[0]
        if jra not in JRA_Requirement:
            JRA_Requirement.append(jra)

    svn_log_txt.writelines("\nSVN_revision_start   :  ")
    svn_log_txt.writelines(str(revision_start.number))
    svn_log_txt.writelines("\nSVN_revision_end     :  ")
    svn_log_txt.writelines(str(revision_end))
    svn_log_txt.writelines("\nlen(JRA_Requirement] : ")
    svn_log_txt.writelines(str(len(JRA_Requirement)))
    svn_log_txt.writelines("\n\n去重后JRA_Requirement      : \n")
    JRA_Requirement.sort()
    for jra in JRA_Requirement:
        svn_log_txt.writelines(jra + "\n")

    print ("去重后需求号 JRA_Requirement")
    print JRA_Requirement
    # 根据log的需求号， 去 JRA上 抓取每一个需要求的LBM
    print "根据log的需求号， 去 JRA上 抓取每一个需要求的LBM"
    get_lbmdll_from_JRA_file_list = []
    get_bin_from_JRA_file_list = []
    total_file_list = []
    lbmdll_from_JRA = "lbmdll_from_JRA.txt"
    cURL_PATH = "D:\\curl-7.55.1-win64\\bin"
    lbmdll_fp = open(lbmdll_from_JRA, "wb")

    file_list_str = '文件清单'
    print "file_list_str =" + file_list_str
    print "type(file_list_str)" + str(type(file_list_str))
    # file_list_gbk = '文件清单'.decode('utf-8')
    # 还需要JRA需求号来定位页面
    for jra in JRA_Requirement:
        lbmdll_fp.writelines("\njra :" + jra + "\n")
        # print "jra requirement number :" + jra
        JRA_URL = "http://192.168.0.221:8080/browse/"
        JRA_account = "zhangqd"
        JRA_password = "zhangqd"
        # jra_test_cmd： curl -S --ftp-ssl-reqd -u zhangqd:zhangqd -o curl_result.txt http://192.168.0.221:8080/browse/ZQWFDJD-36
        cURL_CMD = "curl -S --ftp-ssl-reqd -u "  # 带安全措施-S(security) 请求ssl加密并通过FTP断点传输，保证文件安全且完整
        cURL_CMD += JRA_account  # jra account
        cURL_CMD += ":"
        cURL_CMD += JRA_password  # jra password
        cURL_CMD += " -o "
        curl_result_txt = work_path + "\\curl_result\\" + jra + ".txt"  # 抓取结果存储在本地文件curl_result_txt
        if not os.path.exists(curl_result_txt):
            curl_result_txt = curl_result_txt.decode('utf-8').encode("gb2312")
            # print jra + " gb2312编码切换utf-8编码"
            curl_result_fp = open(curl_result_txt, "wb")
            curl_result_fp.close()
        cURL_CMD += curl_result_txt  # load result to local disk
        cURL_CMD += " "
        cURL_CMD += JRA_URL  # http
        cURL_CMD_temp = cURL_CMD
        cURL_CMD_temp += jra  # cURL命令组建完成
        print "URL_CMD : " + cURL_CMD_temp

        os.chdir(cURL_PATH)  # curl 系统路径
        result = os.system(cURL_CMD_temp)  # 执行cURL命令 ,命令中有对抗网络风险的参数，避免一次通过网络传送消息失败
        if result != 0:
            print  " os.system(cURL_CMD_temp) , return " + str(result)
            print " cURL_CMD 执行出错,请注意异步输出的日志信息\n\n"
            exit(-1)

        os.chdir(work_path)  # 切回工作路径
        # 读取抓取的结果
        fp1 = open(curl_result_txt, "rb")  # jra 抓取的文件清单存储在 curl_result.txt
        file_list_tag = 0
        # 在JRA页面上有两个[需求描述]的类 ，导致我抓取的文件每个需求号有两个[文件清单]类， 请教黄瑞贤，他说在java可以抓取特定的一个
        # 在本段python程序中，使用dos系统下的cURL，
        # dos下cURL不支持正则匹配命令或者说java的特定类匹配方法，只抓取原有的完整页面
        # 出于此原因，得对两份重复的文件清单取舍，这里选择第二份文件清单
        # 服务端都是以kcbp开头， 其中kcbp\lbm 是 lbm**.dll文件  kcbp\bin 是要拷贝的文件
        for my_lbmdll in fp1.readlines():
            my_lbmdll = my_lbmdll.decode('utf-8').encode('gb2312')
            if '文件清单' in my_lbmdll:
                file_list_tag += 1
                continue
            if file_list_tag == 2 and len(my_lbmdll) > 10:
                if re.match(".*\\bkcbp\\\\bin\\b.*", my_lbmdll, re.I):  # 使匹配对大小写不敏感
                    get_lbmdll_temp = my_lbmdll.replace('&nbsp;&nbsp;', '')
                    get_lbmdll_temp = get_lbmdll_temp.rstrip()
                    get_lbmdll_temp += '\n'
                    get_lbmdll_split_list = get_lbmdll_temp.split('\\')
                    get_lbmdll_split_len = len(get_lbmdll_split_list)
                    get_lbmdll = get_lbmdll_split_list[get_lbmdll_split_len - 1]
                    if get_lbmdll not in get_bin_from_JRA_file_list:
                        get_bin_from_JRA_file_list.append(get_lbmdll)
                        lbmdll_fp.writelines(get_lbmdll_temp)
                        total_file_list.append(get_lbmdll_temp)
                        print get_lbmdll_temp
                        continue

                if re.match(".*\\bkcbp\\\\lbm\\b.*", my_lbmdll, re.I):  # 使匹配对大小写不敏感
                    # 文件夹是首字母大小，JRA页面是全小写，需要避免大小写的书写造成判断失效
                    get_lbmdll_temp = my_lbmdll.replace('&nbsp;&nbsp;', '')
                    get_lbmdll_temp = get_lbmdll_temp.rstrip()
                    get_lbmdll_temp += '\n'
                    get_lbmdll_split_list = get_lbmdll_temp.split('\\')
                    get_lbmdll_split_len = len(get_lbmdll_split_list)
                    get_lbmdll = get_lbmdll_split_list[get_lbmdll_split_len - 1]
                    if get_lbmdll not in get_lbmdll_from_JRA_file_list:
                        get_lbmdll_from_JRA_file_list.append(get_lbmdll)  # 只记录lbm dll名称
                        lbmdll_fp.writelines(get_lbmdll_temp)
                        total_file_list.append(get_lbmdll_temp)
                        print get_lbmdll_temp
                        continue

                if "rowForcustomfield_11801" in my_lbmdll:  # JRA需求的页面【文件清单】之后是【单元测试结果】,web标签是“rowForcustomfield_11801”，
                    break

    get_lbmdll_from_JRA_file_list.sort()
    get_bin_from_JRA_file_list.sort()
    total_file_list.sort()
    counter = 0
    total_counter = 0
    lbmdll_fp.write("\n\n**************************************************"
                    "\n\n***   kcbp\\lbm\\  ***\n")
    for i in get_lbmdll_from_JRA_file_list:
        lbmdll_fp.writelines(i)
    counter = len(get_lbmdll_from_JRA_file_list)
    lbmdll_fp.writelines("\n kcbp\\lbm\\ file number:  " + str(counter))
    total_counter += counter
    lbmdll_fp.writelines("\n  file number :  " + str(total_counter))

    lbmdll_fp.write("\n\n***   kcbp\\bin\\   ***\n")
    for i in get_bin_from_JRA_file_list:
        lbmdll_fp.writelines(i)
    counter = len(get_bin_from_JRA_file_list)
    lbmdll_fp.writelines("\n kcbp\\bin\\  file number: " + str(counter))
    total_counter += counter
    lbmdll_fp.writelines("\n file number :  " + str(total_counter))

    lbmdll_fp.writelines("\n**************************************************"
                         "\n\n***  kcbp\\lbm\\  &   kcbp\\bin\\   ***\n")
    print ("\n\n***   kcbp\\lbm\\  &   kcbp\\bin\\   *** :")
    for i in total_file_list:
        print i
        lbmdll_fp.writelines(i)
    lbmdll_fp.writelines("\n file number :  " + str(len(total_file_list)))
    lbmdll_fp.close()

    a = open("3_dll.txt", "wb")  # kcbp\\bin\\***.dll  存储在3_dll.txt
    lbmdlldlllist.sort()
    # 将获取的lbm lbmdlldlllist
    for i in get_lbmdll_from_JRA_file_list:
        i = i.replace(".dll", "")
        if i not in lbmdlldlllist:
            lbmdlldlllist.append(i)  # 去掉 .dll后缀
    lbmdlldlllist.sort()
    for i in lbmdlldlllist:
        a.writelines(i)
    a.close()
    print "get_lbmdll_from_JRA_file_list "
    print get_lbmdll_from_JRA_file_list
    print "lbmdlldlllist"
    print lbmdlldlllist

    a = open("4_bin.txt", "wb")  # 把kcbp\\bin\\的更新的xml 、exe 等文件记录在4_bin.txt

    for i in get_bin_from_JRA_file_list:
        a.writelines(i)
    a.close()
    print ("\n抓取jra文件操作完成!\n\n")
    print "get_bin_from_JRA_file_list "
    print get_bin_from_JRA_file_list

    os.chdir(work_path + "\\lbmdll")
    print (work_path + "\\lbmdll")
    print "first = " + first + "  , 服务端提取JRA上的lbm结束"
if int(first) == 1:
    print "first = " + first + "  ，服务端全部编译开始"
    a = open("BuildTools.bat", "w+")
    a.write('''
@@echo off
echo ==========32位中间件LBM程序重编译(发布必用)==========
echo.

perl build.pl r win32 lbm_acct\lbm_acct.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_bktf\lbm_bktf.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_currentchk\lbm_currentchk.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_debtchg\lbm_debtchg.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_fast\lbm_fast.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_fisacct\lbm_fisacct.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_fisconfig\lbm_fisconfig.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_fismsg\lbm_fismsg.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_fispc\lbm_fispc.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_fisquery\lbm_fisquery.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_fisreport\lbm_fisreport.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_fisrisk\lbm_fisrisk.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_fund\lbm_fund.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_fundmonitor\lbm_fundmonitor.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 plugins\lbm_fundtrans\lbm_fundtrans.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_gen\lbm_gen.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_init\lbm_init.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_jgdz\lbm_jgdz.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_jz30per\lbm_jz30per.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_jzper\lbm_jzper.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_oper\lbm_oper.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_periphery\lbm_periphery.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_position\lbm_position.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_prostat\lbm_prostat.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_public\lbm_public.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_query\lbm_query.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_rprt\lbm_rprt.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_rpt\lbm_rpt.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_rptbs\lbm_rptbs.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_service\lbm_service.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_sett\lbm_sett.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_stat\lbm_stat.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_stk\lbm_stk.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 plugins\lbm_stktrans\lbm_stktrans.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_subscribe\lbm_subscribe.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_swhy\lbm_swhy.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_sys\lbm_sys.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_trandbf\lbm_trandbf.vcxproj
if errorlevel 1 goto err

perl build.pl r win32 lbm_vip\lbm_vip.vcxproj
if errorlevel 1 goto err


echo 全部编译成功
goto end

:err
echo 编译发生错误，请检查程序！

:end

  ''')
    a.close()
    os.system("call BuildTools.bat")
    print("编入版本号完成")
    # os.system('devenv ProjectAll.sln /build "Release|Win32" ')
    # os.system('msbuild ProjectAll.sln /t:Rebuild /p:Configuration=Release /maxcpucount')
    print("编译完成")
