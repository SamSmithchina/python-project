# -*- coding:gb2312 -*-
# python变量分大小写，bat不分大小写，python菜鸟学习网址:http://www.runoob.com/python/python-tutorial.html
import pysvn, os, re, shutil, sys

reload(sys)
sys.setdefaultencoding('gb2312')
print ("python version ", sys.version)


# 2019-01-17 17:51:29
# 过滤 空的bat 和 只有一个 go 或者 空的 sql 的脚本
# 传入 bat或者sql文件路径，
def Filter_Invaild_Files(local_path):
    # 文件以 .sql 结尾
    sql_suffix_pos = local_path.rfind(".sql")
    # 文件以 .bat 结尾
    bat_suffix_pos = local_path.rfind(".bat")
    invalid_flag = 0
    if sql_suffix_pos < 0 and bat_suffix_pos < 0:
        print local_path + "  后缀 异常"
        # 暂时不操作
        invalid_flag = 0
    elif sql_suffix_pos >= 0 or bat_suffix_pos >= 0:
        if sql_suffix_pos >= 0:
            suffix_length = len(local_path) - sql_suffix_pos
        if bat_suffix_pos >= 0:
            suffix_length = len(local_path) - bat_suffix_pos
        if suffix_length != 4:
            print local_path + "  后缀 .sql 异常"
            # 多重后缀, 非.sql结尾 ，比如 AA.sql.dbf ,暂时不操作
            invalid_flag = 0
        else:
            # 检查 文件内容
            sql_file = open(local_path, 'r')
            line_counter = 0
            sentence = ''
            for file_line in sql_file.readlines():
                if file_line == "\n":
                    continue
                line_counter += 1
                sentence += file_line
                if line_counter > 3:  # 读取多行的非\n
                    invalid_flag = 0
                    break
            if line_counter == 0:
                # empty file , delete it
                invalid_flag = 1
            elif line_counter == 1 and sentence == 'go\n' \
                    or line_counter == 2 and sentence == 'go\ngo\n' \
                    or line_counter == 3 and sentence == 'go\ngo\ngo\n':
                # if sentence is qual with 'go\n', delete it
                # 读取了非'\n'行都是'go\n'
                invalid_flag = 1

        sql_file.close()
    #  recognize invalid .bat or .sql fille ,  return 1 means you can delete it
    return invalid_flag


# 清除绝对路径下的空文件夹
delete_folder_list = []
def DelInvaildFolder(local_path):
    file_list = os.listdir(local_path)  # 文件列表
    if not os.path.isdir(local_path):
        # print "not folder : " + str(local_path)
        return
    if len(file_list) == 0:  # 空文件
        os.rmdir(local_path)
        print "delete empty folder : " + str(local_path)
        delete_folder_list.append(local_path)
        return
    for file in file_list:
        full_path = str(local_path + "\\" + file)
        if os.path.isdir(full_path):  # 子层文件夹
            DelInvaildFolder(full_path)


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
# 引用参数end

# 声明全局变量pysvn.Revision,begin

revision_start = pysvn.Revision(pysvn.opt_revision_kind.number, int(Start_version))
revision_start1 = pysvn.Revision(pysvn.opt_revision_kind.number, int(Start_version) + 1)
revision_end = pysvn.Revision(pysvn.opt_revision_kind.head)
peg_revision = pysvn.Revision(pysvn.opt_revision_kind.unspecified)

# 声明全局变量pysvn.Revision,end

# 获取版本，生成工作目录begin
last_path = os.path.basename(mysvn_url)
work_path = workspace + "\\" + last_path
if os.path.exists(work_path):
    print(work_path)
else:
    os.makedirs(work_path)
    # 获取版本，生成工作目录end
    print("获取版本，生成工作目录end")

os.chdir(work_path)  # 切换到工作目录work_path下工作
print ("Start_version ", Start_version)
print ("TO_VERSION ", TO_VERSION)
os.system("svn diff --summarize -r %Start_version%:%TO_VERSION% %mysvn_url%/server>1.txt")

s = open('1.txt', 'r+').read()  # 读取文件1.txt
num1 = len(s)  # 计算文件1.txt字长

print ("file length ： ", num1)  # 打印文件字长的值
if num1 == 0:
    print ("数据库没有代码更新")  # 文件1.txt如果为空,数据库没有代码更新
else:
    print ("数据库代码有更新")  # 文件1.txt如果不为空,数据库代码有更新

    # 更新源码,先把server目录check out到本地begin
    os.chdir(work_path)  # 切换到工作目录下工作
    if os.path.exists("version.txt"):
        print("version.txt已经存在")
        s = open('version.txt', 'w+')
        s.write(SVN_REVISION)
        s.close()
        p = pysvn.Client()
        p.update(work_path + "\\server", revision_end)  # 更新代码svn update.
        print ("更新代码svn update")
    else:
        p = pysvn.Client()
        p.checkout(mysvn_url + "/server", work_path + "\\server")
        print ("server目录check out到本地")
        s = open('version.txt', 'w+')
        s.write(SVN_REVISION)
        s.close()

    # 更新源码,先把 server目录check out到本地end
    print ("更新源码,先把server目录check out到本地end")

    # 生成所需要更新文件的目录结构，方便后面打包编写升级脚本begin
    # len(mysvn_url)计算mysvn_urlL长度
    # 获取路径名: os.path.dirname()
    # 获取文件名：os.path.basename()
    # 分离扩展名：os.path.splitext()

    os.system("svn diff --summarize -r %Start_version%:%SVN_REVISION% server>11.txt")

    newserver = work_path + "\\newserver"
    if os.path.exists(newserver):
        shutil.rmtree(newserver)
        os.mkdir(newserver)  # 清空后再生成目录
    else:
        os.makedirs(newserver)
    os.chdir(newserver)  # 切换到工作目录newserver下工作
    s = open(work_path + "\\11.txt")
    file_list = []
    for line in s.readlines():
        if re.match("A", line) or re.match("M", line):
            file_list.append(line)
            if os.path.exists(os.path.dirname(line[8:])):
                print (os.path.dirname(line[8:]) + "已经存在")
            else:
                print (os.path.dirname(line[8:]))
                os.makedirs(os.path.dirname(line[8:]))
    s.close()
    print ("#生成所需要更新文件的目录结构，方便后面打包编写升级脚本end")
    # 生成所需要更新文件的目录结构，方便后面打包编写升级脚本end

    # 2019-01-17 16:53:58
    # 同一名称文件夹只存在一个级别的规则中， 只是文件夹下的文件会出现在其他规则
    # 级别一：定义全量sql文件规则
    summation = [
        "\\table\\TCrt_rundbProc.sql",
        "\\table\\TCrt_hisdbProc.sql",
        "\\table\\TCrt_reportdbProc.sql",
        "\\proc\\",
        "\\query\\",
        "\\FISUPDATE\\",
        "\\proc_opt\\",
        "\\report\\",
        "\\stat\\"
    ]
    # 级别二：定义增量文件夹下的增量sql文件规则increment_modify和increment_add， 两者同级，
    increment_modify = [  # 修改的增量文件
        "\\query\\querymenu.sql",
        "\\query\\query_add.sql",
        "\\dict\\",
        "\\init\\",
        "\\addorg\\"
    ]
    increment_add = [  # 增加的增量文件，
        "\\query\\querymenu.sql",
        "\\query\\query_add.sql",
        "\\dict\\",
        "\\init\\"
        # "\\addorg\\"
    ]
    # 级别三; table处理方式不一样
    special_table = ["\\table\\"]

    # 需特殊处理文件请严格按照 "\\dir\\file" 从文件夹到最底层文件名方式命名，上述规则支持人为的修改，维护方便;
    # 匹配方式是从文件夹名称到文件，summation与increment*可能存在包含关系，比如query\ 包含query\querymenu.sql，
    # 程序会做summation与increment两重检查，比如待处理query全量文件，必须满足不匹配increment*规则才按全量文件处理
    # 采用逐级过滤的方式， 因为全量文件分类单一处理简单，先筛选出所有全量文件[query,proc,FISUPDATE,proc_opt,report,等等]，
    # 再处理普通增量文件，筛选出[dict,init, addorg, 等等]，
    # 只剩下未处理过的最复杂的table文件，

    # 提取sql文件中缺少的变量定义和赋值
    define_init_variable = ["\\tradedb\\init\\sett_config.sql"]
    # 提取sql文件中 缺少删除关键字的的代码块
    define_delete_variable = ["\\tradedb\\init\\init_pigeonhole.sql"]

    # 记录全量文件
    summation_file = [];
    # 记录修改文件
    increment_modify_file = []
    # 记录增加文件
    increment_add_file = []
    # 记录special_table 文件
    special_table_modify_file = []
    special_table_add_file = []

    # 全量文件处理begin
    os.chdir(newserver)  # 切换到工作目录下工作
    # 处理全量目录 query,proc,FISUPDATE,proc_opt,report,stat,begin
    p = pysvn.Client()
    file_list.sort()
    copy_file_list = list(file_list)
    copy_file_list_2 = list(file_list)
    summation_invalid_file = []
    increment_invalid_file = []
    special_table_invalid_file = []
    invalid_file = []

    for line in file_list:
        available = 0
        # 按照summation规则过滤
        if ".sql" in line and re.match("A", line) or ".sql" in line and re.match("M", line):
            for summation_member in summation:
                pos = line.find(summation_member)
                if pos >= 0:
                    available = 1

                    # 按照increment* 规则纠正全量文件夹下包含的增量文件
                    for increment_member in increment_modify:
                        if line.find(increment_member) < 0:
                            continue  # 未命中规则
                        # 命中规则
                        increment_pos = increment_member.rfind(".sql")  # 反向查找尾缀，
                        if increment_pos == -1:  # increment 规则命中，但不是特殊文件，只是文件夹
                            continue
                        summation_pos = summation_member.rfind(".sql")
                        if summation_pos == -1 and increment_pos >= 0:
                            available = 0  # increment 规则命中，是summation中的特殊文件
                            break  # 后续按increment_member规则处理
                        else:
                            available = 0
                            print ("规则重叠，请检查规则")
                            print ("summation : " + summation_member)
                            print ("increment_modify : " + increment_member)
                            break

                    if 1 == available:
                        for increment_member in increment_add:
                            if line.find(increment_member) < 0:
                                continue  # 未命中规则
                            # 命中规则
                            increment_pos = increment_member.rfind(".sql")  # 反向查找尾缀，
                            if increment_pos == -1:  # increment 规则命中，但不是特殊文件，只是文件夹
                                continue
                            summation_pos = summation_member.rfind(".sql")
                            if summation_pos == -1 and increment_pos >= 0:
                                available = 0  # increment 规则命中，是summation中的特殊文件
                                break  # 后续按increment_member规则处理
                            else:
                                available = 0
                                print ("规则重叠，请检查规则")
                                print ("summation : " + summation_member)
                                print ("increment_modify : " + increment_member)
                                break

                    if 1 == available:
                        for special_member in special_table:
                            if line.find(special_member) < 0:
                                continue  # 未命中规则
                            # 命中规则
                            increment_pos = special_member.rfind(".sql")  # 反向查找尾缀，
                            if increment_pos == -1:  # increment 规则命中，但不是特殊文件，只是文件夹
                                continue
                            summation_pos = summation_member.rfind(".sql")
                            if summation_pos == -1 and increment_pos >= 0:
                                available = 0  # increment 规则命中，是summation中的特殊文件
                                break  # 后续按increment_member规则处理
                            else:
                                available = 0
                                print ("规则重叠，请检查规则")
                                print ("summation : " + summation_member)
                                print ("increment_modify : " + special_member)
                                break
                    # 符合全量文件名规则且不在增量文件中，按全量处理，
                    if 1 == available:
                        break

            if 1 == available:
                # 原因是因为第一行line的后面多了个回车键.#去掉回车符(\r)、换行符(\n)、水平制表符(\t)、垂直制表符(\v)、换页符(\f)）
                svnurlfile = ''.join(line[8:].split())
                # 　print (svnurlfile)
                fp1 = os.path.dirname(svnurlfile)  # 文件所在的上一级目录
                fp2 = svnurlfile.replace('\\', '/')
                svnurl1 = mysvn_url + "/" + fp2
                svnurl = unicode(svnurl1, 'GB2312')  # 转换成svn识别编码，主要是为了能识别中文的svn链接
                localpath1 = newserver + "\\" + fp1
                localpath = unicode(localpath1, 'GB2312')
                # print ("fp1:")
                # print (fp1)
                # print ("svnurl:")
                # print (svnurl)
                # print (localpath)

                p.export(svnurl, localpath, force=True)
                # 过滤 无效bat 和 sql 的脚本
                my_local_path = newserver + "\\" + svnurlfile
                invalid_flag = Filter_Invaild_Files(my_local_path)
                if invalid_flag == 1:
                    print "delete summation invalid file : " + my_local_path
                    summation_invalid_file.append(line)
                    os.remove(my_local_path)
                else:
                    deal_result = re.sub(r"\n", "  ", line).ljust(65, ' ') + summation_member + "\n"
                    # print deal_result
                    summation_file.append(deal_result)
                copy_file_list.remove(line)  # 在副本中移除筛选出的文件

    # 处理全量目录 query,proc,FISUPDATE,proc_opt,report,stat,end
    file_list = list(copy_file_list)  # 去除已处理的文件
    print ("处理全量目录 query,proc,FISUPDATE,proc_opt,report,stat,end")

    # 处理增量目录 query的querymenu.sql,dict,init, addorg , begin
    os.chdir(work_path)
    copy_file_list = list(file_list)  # 拷贝副本
    for line in file_list:
        available = 0
        if ".sql" in line and re.match("M", line):
            for increment_member in increment_modify:
                pos = line.find(increment_member)
                if pos >= 0:
                    available = 1
                    # 去除 special_table中定义的 文件夹
                    for special_member in special_table:
                        if line.find(special_member) < 0:
                            continue  # 未命中规则
                        # 命中规则
                        increment_pos = special_member.rfind(".sql")  # 反向查找尾缀，
                        if increment_pos == -1:  # increment 规则命中，但不是特殊文件，只是文件夹
                            continue
                        summation_pos = increment_member.rfind(".sql")
                        if summation_pos == -1 and increment_pos >= 0:
                            available = 0  # special_table规则命中，是increment中的特殊文件
                            break  # 后续按special_table规则处理
                        else:
                            available = 0
                            print ("规则重叠，请检查规则")
                            print ("summation : " + increment_member)
                            print ("increment_modify : " + special_member)
                            break
                    # 满足increment_modify 规则 且 不在 special__table中 ， 按普通修改的增量文件处理
                    if 1 == available:
                        break

            if 1 == available:
                svnurlfile = ''.join(line[8:].split())  # 去掉回车符(\r)、换行符(\n)、水平制表符(\t)、垂直制表符(\v)、换页符(\f)）
                # print (svnurlfile)  # 下面所有print都是为了方便看日志
                fp1 = os.path.dirname(svnurlfile)
                fp2 = svnurlfile.replace('\\', '/')
                svnurl1 = mysvn_url + "/" + fp2
                svnurl = unicode(svnurl1, 'GB2312')  # 转换成svn识别编码，主要是为了能识别中文的svn链接
                filename = os.path.basename(svnurlfile)
                diff_test = p.diff_peg('', svnurl, peg_revision, revision_start, revision_end,
                                       diff_options=['-b', '-w'], diff_deleted=False,
                                       diff_added=True)  # 版本之间文件的差异,忽略所有空格,空白的变化。
                f = open('media.txt', 'wb+')
                # media.txt是一个内容会变化的文件,先生成写入diff_test，再读取每一行的数据,以二进制方式写入，保证后面sql文件是doc/windows,GB2312格式
                f.write(diff_test)
                # 把差异内容写入media.txt，media中文意思为介质的意思,意思是把文件一个一个有顺序地处理，处理完成一个才轮到下一个文件。所以media.txt的内容只保留处理最后一个文件的内容
                f.close()  # 关闭文件才完成写入动作

                C = p.cat(svnurl, revision_end, peg_revision)
                f1 = open('media1.txt', 'wb+')
                f1.write(C)
                f1.close()
                f1 = open('media1.txt', 'rb')  # 必须关闭文件后才能读取文件
                my_local_path = newserver + "\\" + svnurlfile
                f2 = open(my_local_path, 'wb+')  # 生成文件
                L = set()
                for i in f1.readlines():  # 只要一个use
                    if re.match("^use ", i):  # 只从每一行的开始匹配字符串use,match函数只匹配开头的字符
                        if i.split()[0] not in L:
                            f2.writelines(i.split()[0] + " " + i.split()[1])
                            L.add(i.split()[0])

                f1.close()
                f2.write("\r\n")
                # f2.write("go\r\n")
                f2.close()
                f2 = open(my_local_path, 'a')  # 增加内容
                # f2.write("go\n")  # 换行符\n必须要,往下是换行后再写入内容,否则go与下一句可能会同行
                f = open('media.txt', 'r')  # 必须关闭文件后才能读取文件
                for line1 in f.readlines():
                    if re.match("\+", line1) and not re.match("\+\+\+", line1) \
                            and not re.match("\+ {0,}--", line1) and not re.match("\+use", line1):
                        # 只把+的筛选出来，把+++，@@,+--（注释sql的语句）过滤掉,\+的\为转义字符,match函数只匹配开头的字符,这里也可以用re.search("^+",line1),re.search("\A\+",line1),^+或者\A\+均表示开头匹配。
                        # print (line1)
                        f2.write(line1.lstrip("+"))
                        # 把开头的“+”去掉;循环写完一个文件，再关闭文件，不能才写完一行就关闭文件。Python中的strip用于去除字符串的首尾字符，同理，lstrip用于去除左边的字符，rstrip用于去除右边的字符
                f2.write("go\n")  # 最后加一个go
                f2.close()  # 循环写完一个文件，再关闭文件

                # 过滤 无效bat 和 sql 的脚本
                my_local_path = newserver + "\\" + svnurlfile
                invalid_flag = Filter_Invaild_Files(my_local_path)
                if invalid_flag == 1:
                    print "delete increment invalid file : " + my_local_path
                    increment_invalid_file.append(line)
                    os.remove(my_local_path)
                else:
                    deal_result = re.sub(r"\n", "  ", line).ljust(65, ' ') + increment_member + "\n"
                    increment_modify_file.append(deal_result)
                copy_file_list.remove(line)

        if ".sql" in line and re.match("A", line):
            available = 0
            for increment_member in increment_add:
                pos = line.find(increment_member)
                if pos >= 0:
                    available = 1
                    # 去除 special_table中定义的 文件夹
                    for special_member in special_table:
                        if line.find(special_member) < 0:
                            continue  # 未命中规则
                        # 命中规则
                        increment_pos = special_member.rfind(".sql")  # 反向查找尾缀，
                        if increment_pos == -1:  # increment 规则命中，但不是特殊文件，只是文件夹
                            continue
                        summation_pos = increment_member.rfind(".sql")
                        if summation_pos == -1 and increment_pos >= 0:
                            available = 0  # special_table规则命中，是increment 中的特殊文件
                            break  # 后续按special_table规则处理
                        else:
                            available = 0
                            print ("规则重叠，请检查规则")
                            print ("summation : " + increment_member)
                            print ("increment_modify : " + special_member)
                            break
                    # 满足increment_add 规则 且 不在 special__table中 ， 按普通修改的增量文件处理
                    if 1 == available:
                        break

            if 1 == available:
                svnurlfile = ''.join(line[8:].split())  # 去掉回车符(\r)、换行符(\n)、水平制表符(\t)、垂直制表符(\v)、换页符(\f)）
                # print (svnurlfile)  # 下面所有print都是为了方便看日志
                fp1 = os.path.dirname(svnurlfile)
                fp2 = svnurlfile.replace('\\', '/')
                svnurl1 = mysvn_url + "/" + fp2
                svnurl = unicode(svnurl1, 'GB2312')  # 转换成svn识别编码，主要是为了能识别中文的svn链接
                localpath1 = newserver + "\\" + fp1
                localpath = unicode(localpath1, 'GB2312')
                # print ("fp1:")
                # print (fp1)
                # print ("svnurl:")
                # print (svnurl)
                # print (localpath)
                p.export(svnurl, localpath, force=True)

                # 过滤 无效bat 和 sql 的脚本
                my_local_path = newserver + "\\" + svnurlfile
                invalid_flag = Filter_Invaild_Files(my_local_path)
                if invalid_flag == 1:
                    print "delete increment invalid file : " + my_local_path
                    increment_invalid_file.append(line)
                    os.remove(my_local_path)
                else:
                    deal_result = re.sub(r"\n", "  ", line).ljust(65, ' ') + increment_member + "\n"
                    increment_add_file.append(deal_result)
                copy_file_list.remove(line)

        # 修改、增加变量需要提取变量定义和赋值操作 # 对tradedb\init目录下 符合增量规则且部位无效（空）的文件提取变脸定义和增量
        # 下面代码是简单提取变量定义和赋值，未考虑更复杂的上下文语境
        if 1 == available and 0 == invalid_flag:
            server_source_file = work_path + "\\" + line[8:].split()[0]
            newserver_file = newserver + "\\" + line[8:].split()[0]
            for define_init_file in define_init_variable:
                if define_init_file in line:  # 指定文件
                    f1 = open(server_source_file, 'rb')
                    f2 = open(newserver_file, 'r+')
                    old = f2.read()
                    f2.seek(0)  # 文件指针定义到文件头部
                    for i in f1.readlines():  # 读取该文件
                        if re.match("declare @", i) or re.match("select @", i):
                            # 变量定义 以“declare @”  开头,约定变量赋值以“select @”开头
                            print str(f2.tell()).ljust(5, ' ') + i
                            f2.writelines(i)
                    f2.write(old)
                    f1.close()
                    f2.close()
                    break
            for delete_file in define_delete_variable:
                if delete_file in line:
                    select_pigeonhole = []
                    f1 = open(newserver_file, "rb")
                    for i in f1:
                        sentence = i.strip()
                        if sentence.find("\'select * from") >= 0:  # 以 select * from开头 字符串，为删除的内容主题
                            select_pigeonhole.append(i);
                    f1.close()

                    f2 = open(server_source_file, "rb")
                    pop_flag = 0
                    delete_block = []
                    result_block = []
                    for line_num, sentence in enumerate(f2):
                        if re.match("declare @", sentence) or re.match("select @", sentence):
                            # 变量定义 以“declare @”  开头,约定变量赋值以“select @”开头
                            result_block.append(sentence)
                        else:
                            delete_block.append(sentence)

                        if re.match("delete", sentence):
                            # delete 起始位置
                            delete_begin_line_num = line_num
                            del delete_block
                            delete_block = []
                            delete_block.append(sentence)
                            continue

                        if pop_flag == 0:
                            if len(select_pigeonhole) == 0:
                                break
                            select_pig = select_pigeonhole.pop()
                            pop_flag = 1
                        if pop_flag == 1 and cmp(select_pig, sentence) == 0:
                            pop_flag = 2
                            continue
                        if pop_flag == 2 and sentence.find(
                                "from sysconfig where serverid = @serverid") >= 0:  # 每一块delete 结束位置
                            result_block += list(delete_block)  # 记录结果
                            pop_flag = 0  # 状态位还原
                            continue
                    f2.close()
                    f1 = open(newserver_file, 'wb')
                    for line in result_block:
                        f1.writelines(line)
                    f1.writelines("go")
                    f1.close()
                break
# 处理增量目录 query的querymenu.sql,dict,init, addorg ,end
file_list = list(copy_file_list)

print ("处理增量目录 query的querymenu.sql,dict,init,addorg ,end")

# 处理增量目录 table begin
os.chdir(work_path)
# s = open(work_path + "\\11.txt", 'rb')
copy_file_list = list(file_list)
for line in file_list:  # 这里的line表示mysvn_url地址
    available = 0
    if ".sql" in line and re.match("M", line):
        for special_member in special_table:
            if special_member in line:
                available = 1
                break

        if 1 == available:
            svnurlfile = ''.join(line[8:].split())  # 去掉回车符(\r)、换行符(\n)、水平制表符(\t)、垂直制表符(\v)、换页符(\f)）
            # print (svnurlfile)  # 下面print都是为了方便看日志
            fp1 = os.path.dirname(svnurlfile)
            fp2 = svnurlfile.replace('\\', '/')
            svnurl1 = mysvn_url + "/" + fp2
            svnurl = unicode(svnurl1, 'GB2312')  # 转换成svn识别编码，主要是为了能识别中文的svn链接
            filename = os.path.basename(svnurlfile)  # 目标表的sql脚本名称
            p = pysvn.Client()
            f = open(r"file.txt", "wb+")
            file_text = p.cat(svnurl, revision_end, peg_revision)  # 把目标表sql脚本整个输出
            f.write(file_text)
            f.close()

            # 找出 table 与 table 的行号 begin，即每一个 table 的开始行与结束行

            x = open(r"file.txt", "rb")
            y = open(r"tables.txt", "w+")
            for num, line_1 in enumerate(x):  # 将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标
                if re.match("--====================", line_1):
                    y.write(str(num))
                    y.write("\n")
            y.close()

            # 找出 table 与 table 的行号 end

            # 写入最后一行的行号 begin

            x = open(r"file.txt", "rb")
            y = open(r"tables.txt", "a")
            lastline = x.readlines()
            y.write(str(len(lastline)))
            y.close()

            # 写入最后一行的行号 end

            # 筛选出 table 变化的行 begin
            x = open(r"changelist.txt", "w+")
            changelist = p.annotate(svnurl, revision_start1, revision_end, peg_revision)
            N = 0
            while (N <= len(changelist)):
                x.write(str(changelist[N:N + 1]))
                x.write("\n")
                N = N + 1
            x.close()
            y = open(r"changelist.txt", "r")
            z = open(r"changelinelist.txt", "w+")
            for line_1 in y.readlines():
                t = re.sub("{'date':" + "(.*?)" + "author': u'", '', line_1, flags=re.S)
                if len(t) > 5:
                    t1 = re.compile("number': " + "(.*?)" + ", 'author", flags=re.S)
                    t2 = t1.findall(line_1)
                    z.write(str(t2[0]))
                    z.write("\n")
            z.close()
            # 筛选出 table 变化的行 end

            # 筛选出变化的行所在的表 begin

            # 处理变化行的行号 begin
            y = open(r"tables.txt", "r")
            z = open(r"changelinelist.txt", "r")
            Y = list(y)
            N = 0
            while N < len(Y):
                I = ''.join(Y[N].split())  # 把换行符去掉
                Y[N] = I
                N += 1
            # print (Y)
            Z = list(z)
            N = 0
            while N < len(Z):
                I = ''.join(Z[N].split())  # 把换行符去掉
                Z[N] = I
                N += 1
            # print (Z)

            # 处理变化行的行号 end

            # 每一变化的行的行号跟目标表的开始行与结束行的行号作比较，即找出变化的行所在的表 begin

            N = 0
            M = 0
            y = open(r"tablesout.txt", "wb+")
            while (M < len(Z)):
                while (N < len(Y)):
                    if int(Z[M]) >= int(Y[N]) and int(Z[M]) < int(Y[N + 1]) and int(Z[M]) <> int(len(lastline) - 1):
                        y = open(r"tablesout.txt", "a")
                        # print (Y[N], Z[M], Y[N + 1])
                        y.write(str(Y[N]) + " " + str(Y[N + 1]))
                        y.write("\n")
                        N += 1
                    else:
                        N += 1
                M += 1
                y.close()
                N = N - len(Y)  # 把N的值重新设置为0，一直到M结束
            # 每一变化的行的行号跟目标表的开始行与结束行的行号作比较，即找出变化的行所在的表 end

            # 筛选出变化的行所在的表 end

            # 去掉重复输出的表 begin,即多行在同一个 table 表里变化，只输出一个 table 表，lineset=set()为行的集合
            lineset = set()
            outfile = open(r"tablesout2.txt", "w+")
            for line_1 in open(r"tablesout.txt", "r"):
                if line_1 not in lineset:
                    outfile.write(line_1)
                    lineset.add(line_1)
            outfile.close()
            # 去掉重复的行 end

            # 开始把有变化的 table 表 写入到目标文件 begin

            f1 = open('file.txt', 'rb')  # 必须关闭文件后才能读取文件
            f2 = open(newserver + "\\" + svnurlfile, 'wb+')  # 生成文件
            L = set()
            for i in f1.readlines():  # 只要一个use
                if re.match("use", i):  # 只从每一行的开始匹配字符串use,match函数只匹配开头的字符
                    if i.split()[0] not in L:
                        f2.writelines(i.split()[0] + " " + i.split()[1])
                        L.add(i.split()[0])
            f2.write("\r\n")
            # f2.write("go\r\n")
            f2.close()
            y = open(r"tablesout2.txt", "r")
            for i in y.readlines():
                # print (i)
                line1 = int(i.split()[0])  # 以空格为分割符获取第一个数，即行号
                line2 = int(i.split()[1])  # 以空格为分割符获取第二个数，即行号
                x = open(r"file.txt", "r")
                z = open(newserver + "\\" + svnurlfile, "a")
                for line_1 in x.readlines()[line1:line2]:
                    if not re.match(" {0,}--", line_1):
                        # print (line_1)
                        z.write(line_1)
            # z=open(newserver+"\\"+svnurlfile,"a")
            # z.write("go\n")
            z.close()
            # 对新增加的sql文件进行去注释(/*……*/)处理
            a = open(newserver + "\\" + svnurlfile, 'rb')
            b = a.read()
            c = open(newserver + "\\" + svnurlfile, 'wb')
            d = re.compile(" {0,}/\*.*?\*/", re.S)
            e = re.sub(d, "", b)
            c.write(e)
            c.close()
            a.close()
            # 开始把有变化的 table 表 写入到目标文件 end

            # 过滤 无效bat 和 sql 的脚本
            my_local_path = newserver + "\\" + svnurlfile
            invalid_flag = Filter_Invaild_Files(my_local_path)
            if invalid_flag == 1:
                print "delete invalid file : " + my_local_path
                special_table_invalid_file.append(line)
                os.remove(my_local_path)
            else:
                deal_result = re.sub(r"\n", "  ", line).ljust(65, ' ') + special_member + "\n"
                special_table_modify_file.append(deal_result)
            copy_file_list.remove(line)

    available = 0
    if ".sql" in line and re.match("A", line):
        for special_member in special_table:
            if special_member in line:
                available = 1
                break

        if 1 == available:
            svnurlfile = ''.join(line[8:].split())  # 去掉回车符(\r)、换行符(\n)、水平制表符(\t)、垂直制表符(\v)、换页符(\f)）
            # print (svnurlfile)  # 下面所有print都是为了方便看日志
            fp1 = os.path.dirname(svnurlfile)
            fp2 = svnurlfile.replace('\\', '/')
            svnurl1 = mysvn_url + "/" + fp2
            svnurl = unicode(svnurl1, 'GB2312')  # 转换成svn识别编码，主要是为了能识别中文的svn链接
            localpath1 = newserver + "\\" + fp1
            localpath = unicode(localpath1, 'GB2312')
            # print ("fp1:")
            # print (fp1)
            # print ("svnurl:")
            # print (svnurl)
            # print (localpath)
            p.export(svnurl, localpath, force=True)
            # 对新增加的sql文件进行去注释(/*……*/)处理
            a = open(newserver + "\\" + svnurlfile, 'rb')
            b = a.read()
            c = open(newserver + "\\" + svnurlfile, 'wb')
            d = re.compile("^ {0,}--.*", re.M)
            d1 = re.compile(" {0,}/\*.*?\*/", re.S)
            e = re.sub(d, "", b)
            f = re.sub(d1, "", e)
            c.write(f)
            c.close()
            a.close()

            # 过滤 无效bat 和 sql 的脚本
            my_local_path = newserver + "\\" + svnurlfile
            invalid_flag = Filter_Invaild_Files(my_local_path)
            if invalid_flag == 1:
                print "delete invalid file : " + my_local_path
                special_table_invalid_file.append(line)
                os.remove(my_local_path)
            else:
                deal_result = re.sub(r"\n", "  ", line).ljust(65, ' ') + special_member + "\n"
                special_table_add_file.append(deal_result)
            copy_file_list.remove(line)

# 处理增量目录 table end
file_list = list(copy_file_list)
print ("处理增量目录 table end")

# 输出 优选增量、全量文件按结果到increment_summation
counter = 0
total_counter = 0
print("output result to increment_summation.txt")
increment_summation_txt = work_path + "\\increment_summation.txt"
s = open(increment_summation_txt, 'w')

copy_file_list_2.sort()
for i in copy_file_list_2:
    # print i
    if ".sql" not in i:
        counter += 1
    s.write(i)
s.write("\n11.txt ***.bat have =  " + str(counter))
print ("\n11.txt ***.bat have =  " + str(counter))
s.write("\n11.txt ***.sql total number =  " + str(len(copy_file_list_2) - counter))
print ("\n11.txt ***.sql total number =  " + str(len(copy_file_list_2) - counter))

counter = 0
s.write("\n\nsummation_file 全量文件")
s.write("\n[\n")
for i in summation:
    s.write("         " + i + "\n")
s.write("]\n")
summation_file.sort()
for i in summation_file:
    s.write(i)
counter = len(summation_file)
total_counter += counter
s.write("\nfile number = " + str(counter))
s.write("\n文件数量 = " + str(total_counter))

s.write("\n\nincrement file 增量文件")
s.write("\n[\n")
for i in increment_modify:
    s.write("         " + i + "\n")
s.write("]\n")
counter = 0
increment_file = increment_add_file + increment_modify_file
increment_file.sort()
for i in increment_file:
    s.write(i)
counter = len(increment_file)
total_counter += counter
s.write("\nfile number = " + str(counter))
s.write("\n文件数量 = " + str(total_counter))

s.write("\n\nspecial_table 增量\\table\\")
s.write("\n[\n")
for i in special_table:
    s.write("         " + i + "\n")
s.write("]\n")
counter = 0
special_table_file = special_table_add_file + special_table_modify_file
special_table_file.sort()
for i in special_table_file:
    s.write(i)
counter = len(special_table_file)
total_counter += counter
s.write("\nfile number = " + str(counter))
s.write("\n文件数量 = " + str(total_counter))

# 以上文件中 无效文件 invalid_file
counter = 0;
s.write("\n\n以上文件中无效的文件有 invalid file \n ")
summation_invalid_file.sort()
increment_invalid_file.sort()
special_table_invalid_file.sort()
invalid_file = summation_invalid_file + increment_invalid_file + special_table_invalid_file
for i in invalid_file:
    s.write(i)
counter = len(invalid_file)
total_counter += counter
s.write("\ninvalid file = " + str(counter))
s.write("\ntotal number 全部文件数量 = " + str(total_counter))

# 清空 \6.7.9.0_0.1.0\newserver路径下的空文件夹
DelInvaildFolder(newserver)
s.writelines("\n\n删除空文件夹\n")
for delete_folder in delete_folder_list:
    s.writelines(delete_folder)
s.close()

s = open(increment_summation_txt, 'r')
for i in s.readlines():
    print i
s.close()

# 清理 11.txt 中的无效文件
s = open("11.txt", 'wb')
for i in copy_file_list_2:
    if i not in invalid_file:
        s.writelines(i)
s.close()

# 清空升级包目录再生成目录 begin
if os.path.exists(PATCH_NAME + "\\server"):
    shutil.rmtree(PATCH_NAME + "\\server")
    shutil.rmtree(PATCH_NAME + "\\doc")
    os.makedirs(PATCH_NAME + "\\server")
    os.makedirs(PATCH_NAME + "\\doc")
else:
    os.makedirs(PATCH_NAME + "\\server")
    os.makedirs(PATCH_NAME + "\\doc")
# 清空升级包目录再生成目录 end

# sqlsh.exe 处理
os.chdir(work_path + "\\server\\tradedb")
if os.path.exists(work_path + "\\server\\tradedb\\sqlsh.exe"):
    shutil.copy(work_path + "\\server\\tradedb\\sqlsh.exe", work_path + "\\newserver\\server")
else:
    print(work_path + "\\server\\tradedb\\sqlsh.exe" + "不存在")
# PatchVer.sql 处理
os.chdir(work_path + "\\newserver\\server")
a = open('PatchVer.sql', 'w+')
a.write('''exec nb_add_version \'''' + Sql_version + '''\'go''')
a.close()

# 升级脚本文件处理
# 01_交易服务器(run).bat begin
os.chdir(work_path + "\\newserver\\server")
# run顺序列表，列表特点之一是有顺序的，以后顺序变了，可以调一下以下列表的顺序，或者有新的目录增加，按照先后顺序在列表中添加即可。
orderrunlist = ["tradedb\\table\\", "tradedb\\stat\\", "tradedb\\init\\", "tradedb\\dict\\", "tradedb\\query\\",
                "tradedb\\proc_opt\\", "tradedb\\proc\\", "tradedb\\FISUPDATE\\proc\\",
                "tradedb\\interface_vip\\table\\", "tradedb\\interface_vip\\init\\",
                "tradedb\\interface_vip\\dict\\", "tradedb\\interface_vip\\query\\",
                "tradedb\\interface_vip\\proc\\", "tradedb\\report\\", "tradedb\\DBCONTROL\\table\\",
                "tradedb\\DBCONTROL\\init\\", "tradedb\\DBCONTROL\\proc\\", "tradedb\\init\\datafix.sql"]
# 目录存在，则写入Q1_交易.bat文件，哪些目录该写入哪个bat按打包手册规定的为准。
# 定义文件夹内部优先级顺序，统一风格，支持优先级自定义,未定义优先级的文件不做特殊处理
file_order_list = ["TCrt", "proc"]
if os.path.exists(work_path + "\\newserver\\server\\tradedb"):
    b = open("01_交易服务器(run).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    新一代Win版 融资融券''' + Sql_version + '''升级包  交易服务器(run).bat
@ECHO ------------------------------------------------------------------------
@ECHO 为保证正常执行升级脚本请注意以下几点：
@ECHO    1. 请关闭所有的数据库连接
@ECHO    2. 本升级包有创建新的表,请停止你的数据库复制
@ECHO ========================================================================
pause
sqlsh -U交易库用户名 -P交易库密码 -S交易库服务器地址 -drun -i .\PatchVer.sql

''')
    b.close()
    # 从顺序列表orderrunlist中获取数组迭代写入bat,存在则写入，不存在则跳过，每一个顺序迭代，都使用sort正序进行排序，方便前后两个版本对比bat，避免顺序错乱不好对比。
    for i in orderrunlist:
        print "\n======================================================================"
        print("run顺序：" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("01_交易服务器(run).bat", "a")
        drun = ("noexist")
        lrun = []
        for line in a.readlines():
            if "server\\tradedb" in line and re.match("A", line) or "server\\tradedb" in line and re.match("M",
                                                                                                           line):
                if i in line:
                    lrun.append(line)

        # 按定义的文件优先顺序排序
        run_list_in_order = [[] for i in range(len(file_order_list))]  # 二维数组分别存放不同优先级的文件
        # 其他未定义优先级的文件
        run_list_out_of_order = []
        print "排序数组初始化状态 ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lrun ", lrun

        for subfile in lrun:
            exist_flag = 0
            pos = subfile.rfind("\\")  # 取文件名
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # 按定义优先级记录文件在数组run_list_in_order
                    break
            # 未定义优先级的存在另一个数组run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # 当前文件夹下所以文件处理完毕

        lrun = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lrun += run_list_in_order[cursor]  # 合并数组
        # 未定义优先级的文件按名字正序排序
        run_list_out_of_order.sort()
        print "未定义优先级 ", run_list_out_of_order
        lrun += run_list_out_of_order  # 合并数组
        print "排序后结果"
        print lrun
        print "======================================================================\n"

        for i in lrun:
            c.write(re.sub(r"\r", "", i))
            drun = ("exist")
        if drun == ("exist"):  # 按书写规范，有每一个顺序结束后换行进行分类。
            c.write("\n")
    c = open("01_交易服务器(run).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("01_交易服务器(run).bat", "rb")
    f = c.read()
    c1 = open("01_交易服务器(run).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U交易库用户名 -P交易库密码 -S交易库服务器地址 -drun -i .\\", f)  # 按打包手册规范书写，re.sub字符查找并替换，详细百度re.sub
    c1.write(q)
    c1.close()
    # 把前面的datafix.sql去掉 begin
    a = open("01_交易服务器(run).bat", "rb")
    b = []  # 建立一个空列表用来存放Q1_交易.bat每一行
    for i in a.readlines():
        b.append(i)
    for i in b:
        if "datafix.sql" in i:
            I = i
            b.remove(I)  # remove只去除匹配的那一个datafix.sql
            break  # 只找前面一个
    print(b)
    # 把前面的datafix.sql去掉 end
    c = open("01_交易服务器(run).bat", "wb")
    for i in b:
        c.write(i)
    c.close()
# 01_交易服务器(run).bat end
# 02_交易服务器(report).bat begin
os.chdir(work_path + "\\newserver\\server")
# run顺序列表，列表特点之一是有顺序的，以后顺序变了，可以调一下以下列表的顺序，或者有新的目录增加，按照先后顺序在列表中添加即可。
orderrunlist = ["reportdb\\table\\", "reportdb\\proc\\"]
# 目录存在，则写入Q1_交易.bat文件，哪些目录该写入哪个bat按打包手册规定的为准。
# 定义文件夹内部优先级顺序，统一风格，支持优先级自定义,未定义优先级的文件不做特殊处理
file_order_list = ["TCrt", "proc"]
if os.path.exists(work_path + "\\newserver\\server\\reportdb"):
    b = open("02_交易服务器(report).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    新一代Win版 融资融券''' + Sql_version + '''升级包  交易服务器(report).bat
@ECHO ------------------------------------------------------------------------
@ECHO 为保证正常执行升级脚本请注意以下几点：
@ECHO    1. 请关闭所有的数据库连接
@ECHO    2. 本升级包有创建新的表,请停止你的数据库复制
@ECHO ========================================================================
pause

''')
    b.close()
    # 从顺序列表orderrunlist中获取数组迭代写入bat,存在则写入，不存在则跳过，每一个顺序迭代，都使用sort正序进行排序，方便前后两个版本对比bat，避免顺序错乱不好对比。
    for i in orderrunlist:
        print "\n======================================================================"
        print("run顺序：" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("02_交易服务器(report).bat", "a")
        drun = ("noexist")
        lrun = []
        for line in a.readlines():
            if "server\\reportdb" in line and re.match("A", line) or "server\\reportdb" in line and re.match("M",
                                                                                                             line):
                if i in line:
                    lrun.append(line)

        # 按定义的文件优先顺序排序
        run_list_in_order = [[] for i in range(len(file_order_list))]  # 二维数组分别存放不同优先级的文件
        # 其他未定义优先级的文件
        run_list_out_of_order = []
        print "排序数组初始化状态 ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lrun ", lrun

        for subfile in lrun:
            exist_flag = 0
            pos = subfile.rfind("\\")  # 取文件名
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # 按定义优先级记录文件在数组run_list_in_order
                    break
            # 未定义优先级的存在另一个数组run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # 当前文件夹下所以文件处理完毕

        lrun = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lrun += run_list_in_order[cursor]  # 合并数组
        # 未定义优先级的文件按名字正序排序
        run_list_out_of_order.sort()
        print "未定义优先级 ", run_list_out_of_order
        lrun += run_list_out_of_order  # 合并数组
        print "排序后结果"
        print lrun
        print "======================================================================\n"

        for i in lrun:
            c.write(re.sub(r"\r", "", i))
            drun = ("exist")
        if drun == ("exist"):  # 按书写规范，有每一个顺序结束后换行进行分类。
            c.write("\n")
    c = open("02_交易服务器(report).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("02_交易服务器(report).bat", "rb")
    f = c.read()
    c1 = open("02_交易服务器(report).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U交易库用户名 -P交易库密码 -S交易库服务器地址 -dreport -i .\\", f)  # 按打包手册规范书写，re.sub字符查找并替换，详细百度re.sub
    c1.write(q)
    c1.close()
# 02_交易服务器(report).bat end
# 03_风控服务器(run).bat begin
os.chdir(work_path + "\\newserver\\server")
# 风控run顺序列表，列表特点之一是有顺序的，以后顺序变了，可以调一下以下列表的顺序，或者有新的目录增加，按照先后顺序在列表中添加即可。
orderfkrunlist = ["tradedb\\table\\", "tradedb\\stat\\", "tradedb\\init\\", "tradedb\\dict\\", "tradedb\\query\\",
                  "tradedb\\proc_opt\\", "tradedb\\proc\\", "tradedb\\FISUPDATE\\proc\\",
                  "tradedb\\interface_vip\\table\\", "tradedb\\interface_vip\\init\\",
                  "tradedb\\interface_vip\\dict\\", "tradedb\\interface_vip\\query\\",
                  "tradedb\\interface_vip\\proc\\", "tradedb\\report\\", "tradedb\\DBCONTROL\\table\\",
                  "tradedb\\DBCONTROL\\init\\", "tradedb\\DBCONTROL\\proc\\"]
# 目录存在，则写入Q1_风控.bat文件，哪些目录该写入哪个bat按打包手册规定的为准。

# 定义文件夹内部优先级顺序，统一风格，支持优先级自定义,未定义优先级的文件不做特殊处理
file_order_list = ["TCrt", "proc"]

if os.path.exists(work_path + "\\newserver\\server\\tradedb"):
    b = open("03_风控服务器(run).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    新一代Win版 融资融券''' + Sql_version + '''升级包  风控服务器(run).bat
@ECHO ------------------------------------------------------------------------
@ECHO 为保证正常执行升级脚本请注意以下几点：
@ECHO    1. 请关闭所有的数据库连接
@ECHO    2. 本升级包有创建新的表,请停止你的数据库复制
@ECHO ========================================================================
pause
sqlsh -U风控库用户名 -P风控库密码 -S风控库服务器地址 -drun -i .\PatchVer.sql

''')
    b.close()
    # 从顺序列表orderfkrunlist中获取数组迭代写入bat,存在则写入，不存在则跳过，每一个顺序迭代，都使用sort正序进行排序，方便前后两个版本对比bat，避免顺序错乱不好对比。
    for i in orderfkrunlist:
        print "\n======================================================================"
        print("fkrun顺序：" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("03_风控服务器(run).bat", "a")
        dfkrun = ("noexist")
        lfkrun = []
        for line in a.readlines():
            if "server\\tradedb" in line and re.match("A", line) or "server\\tradedb" in line and re.match("M",
                                                                                                           line):
                if i in line:
                    lfkrun.append(line)

                # 按定义的文件优先顺序排序
        run_list_in_order = [[] for i in range(len(file_order_list))]  # 二维数组分别存放不同优先级的文件
        # 其他未定义优先级的文件
        run_list_out_of_order = []
        print "排序数组初始化状态 ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lfkrun ", lfkrun

        for subfile in lfkrun:
            exist_flag = 0
            pos = subfile.rfind("\\")  # 取文件名
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # 按定义优先级记录文件在数组run_list_in_order
                    break
            # 未定义优先级的存在另一个数组run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # 当前文件夹下所以文件处理完毕

        lfkrun = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lfkrun += run_list_in_order[cursor]  # 合并数组
        # 未定义优先级的文件按名字正序排序
        run_list_out_of_order.sort()
        print "未定义优先级 ", run_list_out_of_order
        lfkrun += run_list_out_of_order  # 合并数组
        print "排序后结果"
        print lfkrun
        print "======================================================================\n"

        for i in lfkrun:
            c.write(re.sub(r"\r", "", i))
            dfkrun = ("exist")
        if dfkrun == ("exist"):  # 按书写规范，有每一个顺序结束后换行进行分类。
            c.write("\n")
    c = open("03_风控服务器(run).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("03_风控服务器(run).bat", "rb")
    f = c.read()
    c1 = open("03_风控服务器(run).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U风控库用户名 -P风控库密码 -S风控库服务器地址 -drun -i .\\", f)  # 按打包手册规范书写，re.sub字符查找并替换，详细百度re.sub
    c1.write(q)
    c1.close()
    # 把前面的datafix.sql去掉 把后面的datafix_riskdb.sql begin
    a = open("03_风控服务器(run).bat", "rb")
    b = []  # 建立一个空列表用来存放Q1_风控.bat每一行
    for i in a.readlines():
        b.append(i)
    for i in b:
        if "datafix.sql" in i:
            print("I0:" + i)
            I0 = i
            b.remove(I0)  # remove只去除匹配的那一个datafix.sql
            break  # 只找前面一个
    I1 = ''
    datafix = ''
    for i in b:
        if "datafix_riskdb.sql" in i:
            I1 = i
            datafix = ('exist')
    if datafix == 'exist':
        for i in enumerate(b):
            if i[1] == I1:
                I2 = i[0]
        del b[I2]
    print(b)
    # 把前面的datafix.sql去掉 把后面的datafix_riskdb.sql begin end
    c = open("03_风控服务器(run).bat", "wb")
    for i in b:
        c.write(i)
        print(i)
    c.close()
# 03_风控服务器(run).bat end
# 04_风控服务器(riskdb).bat begin
os.chdir(work_path + "\\newserver\\server")
# 风控run顺序列表，列表特点之一是有顺序的，以后顺序变了，可以调一下以下列表的顺序，或者有新的目录增加，按照先后顺序在列表中添加即可。
orderfkrunlist = ["riskdb\\init\\datafix_riskdb.sql", "riskdb\\table\\", "riskdb\\init\\", "riskdb\\proc\\"]
# 目录存在，则写入04_风控服务器(riskdb).bat文件，哪些目录该写入哪个bat按打包手册规定的为准。

# 定义文件夹内部优先级顺序，统一风格，支持优先级自定义,未定义优先级的文件不做特殊处理
file_order_list = ["TCrt", "proc"]

if os.path.exists(work_path + "\\newserver\\server\\riskdb"):
    b = open("04_风控服务器(riskdb).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    新一代Win版 融资融券''' + Sql_version + '''升级包  风控服务器(riskdb).bat
@ECHO ------------------------------------------------------------------------
@ECHO 为保证正常执行升级脚本请注意以下几点：
@ECHO    1. 请关闭所有的数据库连接
@ECHO    2. 本升级包有创建新的表,请停止你的数据库复制
@ECHO ========================================================================
pause

''')
    b.close()
    # 从顺序列表orderfkrunlist中获取数组迭代写入bat,存在则写入，不存在则跳过，每一个顺序迭代，都使用sort正序进行排序，方便前后两个版本对比bat，避免顺序错乱不好对比。
    for i in orderfkrunlist:
        print "\n======================================================================"
        print("fkrun顺序：" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("04_风控服务器(riskdb).bat", "a")
        dfkrun = ("noexist")
        lfkrun = []
        for line in a.readlines():
            if "server\\riskdb" in line and re.match("A", line) or "server\\riskdb" in line and re.match("M", line):
                if i in line:
                    lfkrun.append(line)

            # 按定义的文件优先顺序排序
        run_list_in_order = [[] for i in range(len(file_order_list))]  # 二维数组分别存放不同优先级的文件
        # 其他未定义优先级的文件
        run_list_out_of_order = []
        print "排序数组初始化状态 ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lfkrun ", lfkrun

        for subfile in lfkrun:
            exist_flag = 0
            pos = subfile.rfind("\\")  # 取文件名
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # 按定义优先级记录文件在数组run_list_in_order
                    break
            # 未定义优先级的存在另一个数组run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # 当前文件夹下所以文件处理完毕

        lfkrun = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lfkrun += run_list_in_order[cursor]  # 合并数组
        # 未定义优先级的文件按名字正序排序
        run_list_out_of_order.sort()
        print "未定义优先级 ", run_list_out_of_order
        lfkrun += run_list_out_of_order  # 合并数组
        print "排序后结果"
        print lfkrun
        print "======================================================================\n"

        for i in lfkrun:
            c.write(re.sub(r"\r", "", i))
            dfkrun = ("exist")
        if dfkrun == ("exist"):  # 按书写规范，有每一个顺序结束后换行进行分类。
            c.write("\n")
    c = open("04_风控服务器(riskdb).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("04_风控服务器(riskdb).bat", "rb")
    f = c.read()
    c1 = open("04_风控服务器(riskdb).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U风控库用户名 -P风控库密码 -S风控库服务器地址 -driskdb -i .\\", f)  # 按打包手册规范书写，re.sub字符查找并替换，详细百度re.sub
    c1.write(q)
    c1.close()
    # 把前面的datafix.sql去掉 把后面的datafix_riskdb.sql begin
    a = open("04_风控服务器(riskdb).bat", "rb")
    b = []  # 建立一个空列表用来存放Q1_风控.bat每一行
    for i in a.readlines():
        b.append(i)
    for i in b:
        if "datafix.sql" in i:
            print("I0:" + i)
            I0 = i
            b.remove(I0)  # remove只去除匹配的那一个datafix.sql
            break  # 只找前面一个
    I1 = ''
    datafix = ''
    for i in b:
        if "datafix_riskdb.sql" in i:
            I1 = i
            datafix = ('exist')
    if datafix == 'exist':
        for i in enumerate(b):
            if i[1] == I1:
                I2 = i[0]
        del b[I2]
    print(b)
    # 把前面的datafix.sql去掉 把后面的datafix_riskdb.sql begin end
    c = open("04_风控服务器(riskdb).bat", "wb")
    for i in b:
        c.write(i)
        print(i)
    c.close()
# 04_风控服务器(riskdb).bat end
# 05_历史服务器(run).bat begin
# his顺序列表 begin
orderhislist = ["\\TCrt_rundbProc.sql", "\\Thist_run.sql", "\\THist_run_credit.sql", "\\THist_run_openfund.sql"]
# 定义文件夹内部优先级顺序，统一风格，支持优先级自定义,未定义优先级的文件不做特殊处理
file_order_list = ["TCrt", "proc"]

if os.path.exists(work_path + "\\newserver\\server\\querydb"):
    b = open("05_历史服务器(run).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    新一代Win版 融资融券''' + Sql_version + '''升级包  历史服务器(run).bat
@ECHO ------------------------------------------------------------------------
@ECHO 为保证正常执行升级脚本请注意以下几点：
@ECHO    1. 请关闭所有的数据库连接
@ECHO    2. 本升级包有创建新的表,请停止你的数据库复制
@ECHO ========================================================================
pause
''')
    b.close()
    for i in orderhislist:
        print "\n======================================================================"
        print("his顺序：" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("05_历史服务器(run).bat", "a")
        dhis = ("noexist")
        lhis = []
        for line in a.readlines():
            if "server\\querydb" in line and re.match("A", line) or "server\\querydb" in line and re.match("M",
                                                                                                           line):
                if i in line:
                    lhis.append(line)

        # 按定义的文件优先顺序排序
        run_list_in_order = [[] for i in range(len(file_order_list))]  # 二维数组分别存放不同优先级的文件
        # 其他未定义优先级的文件
        run_list_out_of_order = []
        print "排序数组初始化状态 ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lhis ", lhis

        for subfile in lhis:
            exist_flag = 0
            pos = subfile.rfind("\\")  # 取文件名
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # 按定义优先级记录文件在数组run_list_in_order
                    break
            # 未定义优先级的存在另一个数组run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # 当前文件夹下所以文件处理完毕

        lhis = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lhis += run_list_in_order[cursor]  # 合并数组
        # 未定义优先级的文件按名字正序排序
        run_list_out_of_order.sort()
        print "未定义优先级 ", run_list_out_of_order
        lhis += run_list_out_of_order  # 合并数组
        print "排序后结果"
        print lhis
        print "======================================================================\n"

        for i in lhis:
            c.write(re.sub(r"\r", "", i))
            dhis = ("exist")
        if dhis == ("exist"):
            c.write("\n")
    c = open("05_历史服务器(run).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("05_历史服务器(run).bat", "rb")
    f = c.read()
    c1 = open("05_历史服务器(run).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U历史库用户名 -P历史库密码 -S历史库服务器地址 -drun -i .\\", f)
    print(q)
    c1.write(q)
    c1.close()
    # 05_历史服务器(run).bat end
# 06_历史服务器(his).bat begin
# his顺序列表 begin
orderhislist = ["querydb\\hisdb\\table\\", "querydb\\hisdb\\init\\", "querydb\\hisdb\\FISUPDATE\\proc\\"]

# 定义文件夹内部优先级顺序，统一风格，支持优先级自定义,未定义优先级的文件不做特殊处理
file_order_list = ["TCrt", "proc"]

if os.path.exists(work_path + "\\newserver\\server\\querydb"):
    b = open("06_历史服务器(his).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    新一代Win版 融资融券''' + Sql_version + '''升级包  历史服务器(his).bat
@ECHO ------------------------------------------------------------------------
@ECHO 为保证正常执行升级脚本请注意以下几点：
@ECHO    1. 请关闭所有的数据库连接
@ECHO    2. 本升级包有创建新的表,请停止你的数据库复制
@ECHO ========================================================================
pause
''')
    b.close()
    for i in orderhislist:
        print "\n======================================================================"
        print("his顺序：" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("06_历史服务器(his).bat", "a")
        dhis = ("noexist")
        lhis = []
        for line in a.readlines():
            if "server\\querydb" in line and re.match("A", line) or "server\\querydb" in line and re.match("M",
                                                                                                           line):
                if "\\hisdb\\TCrt_rundbProc.sql" not in line and re.match("A",
                                                                          line) or "\\hisdb\\TCrt_rundbProc.sql" not in line and re.match(
                    "M", line):
                    if "\\hisdb\\Thist_run.sql" not in line and re.match("A",
                                                                         line) or "\\hisdb\\Thist_run.sql" not in line and re.match(
                        "M", line):
                        if "\\hisdb\\THist_run_credit.sql" not in line and re.match("A",
                                                                                    line) or "\\hisdb\\THist_run_credit.sql" not in line and re.match(
                            "M", line):
                            if "\\hisdb\\THist_run_openfund.sql" not in line and re.match("A",
                                                                                          line) or "\\hisdb\\THist_run_openfund.sql" not in line and re.match(
                                "M", line):
                                if i in line:
                                    lhis.append(line)

        # 按定义的文件优先顺序排序
        run_list_in_order = [[] for i in range(len(file_order_list))]  # 二维数组分别存放不同优先级的文件
        # 其他未定义优先级的文件
        run_list_out_of_order = []
        print "排序数组初始化状态 ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lhis ", lhis

        for subfile in lhis:
            exist_flag = 0
            pos = subfile.rfind("\\")  # 取文件名
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # 按定义优先级记录文件在数组run_list_in_order
                    break
            # 未定义优先级的存在另一个数组run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # 当前文件夹下所以文件处理完毕

        lhis = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lhis += run_list_in_order[cursor]  # 合并数组
        # 未定义优先级的文件按名字正序排序
        run_list_out_of_order.sort()
        print "未定义优先级 ", run_list_out_of_order
        lhis += run_list_out_of_order  # 合并数组
        print "排序后结果"
        print lhis
        print "======================================================================\n"

        for i in lhis:
            c.write(re.sub(r"\r", "", i))
            dhis = ("exist")
        if dhis == ("exist"):
            c.write("\n")
    c = open("06_历史服务器(his).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("06_历史服务器(his).bat", "rb")
    f = c.read()
    c1 = open("06_历史服务器(his).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U历史库用户名 -P历史库密码 -S历史库服务器地址 -dhis -i .\\", f)
    print(q)
    c1.write(q)
    c1.close()
    # 06_历史服务器(his).bat end
