# -*- coding:gb2312 -*-
# python�����ִ�Сд��bat���ִ�Сд��python����ѧϰ��ַ:http://www.runoob.com/python/python-tutorial.html
import pysvn, os, re, shutil, sys

reload(sys)
sys.setdefaultencoding('gb2312')
print ("python version ", sys.version)


# 2019-01-17 17:51:29
# ���� �յ�bat �� ֻ��һ�� go ���� �յ� sql �Ľű�
# ���� bat����sql�ļ�·����
def Filter_Invaild_Files(local_path):
    # �ļ��� .sql ��β
    sql_suffix_pos = local_path.rfind(".sql")
    # �ļ��� .bat ��β
    bat_suffix_pos = local_path.rfind(".bat")
    invalid_flag = 0
    if sql_suffix_pos < 0 and bat_suffix_pos < 0:
        print local_path + "  ��׺ �쳣"
        # ��ʱ������
        invalid_flag = 0
    elif sql_suffix_pos >= 0 or bat_suffix_pos >= 0:
        if sql_suffix_pos >= 0:
            suffix_length = len(local_path) - sql_suffix_pos
        if bat_suffix_pos >= 0:
            suffix_length = len(local_path) - bat_suffix_pos
        if suffix_length != 4:
            print local_path + "  ��׺ .sql �쳣"
            # ���غ�׺, ��.sql��β ������ AA.sql.dbf ,��ʱ������
            invalid_flag = 0
        else:
            # ��� �ļ�����
            sql_file = open(local_path, 'r')
            line_counter = 0
            sentence = ''
            for file_line in sql_file.readlines():
                if file_line == "\n":
                    continue
                line_counter += 1
                sentence += file_line
                if line_counter > 3:  # ��ȡ���еķ�\n
                    invalid_flag = 0
                    break
            if line_counter == 0:
                # empty file , delete it
                invalid_flag = 1
            elif line_counter == 1 and sentence == 'go\n' \
                    or line_counter == 2 and sentence == 'go\ngo\n' \
                    or line_counter == 3 and sentence == 'go\ngo\ngo\n':
                # if sentence is qual with 'go\n', delete it
                # ��ȡ�˷�'\n'�ж���'go\n'
                invalid_flag = 1

        sql_file.close()
    #  recognize invalid .bat or .sql fille ,  return 1 means you can delete it
    return invalid_flag


# �������·���µĿ��ļ���
delete_folder_list = []
def DelInvaildFolder(local_path):
    file_list = os.listdir(local_path)  # �ļ��б�
    if not os.path.isdir(local_path):
        # print "not folder : " + str(local_path)
        return
    if len(file_list) == 0:  # ���ļ�
        os.rmdir(local_path)
        print "delete empty folder : " + str(local_path)
        delete_folder_list.append(local_path)
        return
    for file in file_list:
        full_path = str(local_path + "\\" + file)
        if os.path.isdir(full_path):  # �Ӳ��ļ���
            DelInvaildFolder(full_path)


# ���ò���begin
# ��ȡ�����û�������:os.getenv() ��os.putenv()
PATCH_NAME = os.getenv("PATCH_NAME")
mysvn_url = os.getenv("mysvn_url")
Start_version = os.getenv("Start_version")
TO_VERSION = os.getenv("TO_VERSION")
Client_version = os.getenv("Client_version")
Lbmdll_version = os.getenv("Lbmdll_version")
Sql_version = os.getenv("Sql_version")
workspace = os.getenv("workspace")
SVN_REVISION = os.getenv("SVN_REVISION")
# ���ò���end

# ����ȫ�ֱ���pysvn.Revision,begin

revision_start = pysvn.Revision(pysvn.opt_revision_kind.number, int(Start_version))
revision_start1 = pysvn.Revision(pysvn.opt_revision_kind.number, int(Start_version) + 1)
revision_end = pysvn.Revision(pysvn.opt_revision_kind.head)
peg_revision = pysvn.Revision(pysvn.opt_revision_kind.unspecified)

# ����ȫ�ֱ���pysvn.Revision,end

# ��ȡ�汾�����ɹ���Ŀ¼begin
last_path = os.path.basename(mysvn_url)
work_path = workspace + "\\" + last_path
if os.path.exists(work_path):
    print(work_path)
else:
    os.makedirs(work_path)
    # ��ȡ�汾�����ɹ���Ŀ¼end
    print("��ȡ�汾�����ɹ���Ŀ¼end")

os.chdir(work_path)  # �л�������Ŀ¼work_path�¹���
print ("Start_version ", Start_version)
print ("TO_VERSION ", TO_VERSION)
os.system("svn diff --summarize -r %Start_version%:%TO_VERSION% %mysvn_url%/server>1.txt")

s = open('1.txt', 'r+').read()  # ��ȡ�ļ�1.txt
num1 = len(s)  # �����ļ�1.txt�ֳ�

print ("file length �� ", num1)  # ��ӡ�ļ��ֳ���ֵ
if num1 == 0:
    print ("���ݿ�û�д������")  # �ļ�1.txt���Ϊ��,���ݿ�û�д������
else:
    print ("���ݿ�����и���")  # �ļ�1.txt�����Ϊ��,���ݿ�����и���

    # ����Դ��,�Ȱ�serverĿ¼check out������begin
    os.chdir(work_path)  # �л�������Ŀ¼�¹���
    if os.path.exists("version.txt"):
        print("version.txt�Ѿ�����")
        s = open('version.txt', 'w+')
        s.write(SVN_REVISION)
        s.close()
        p = pysvn.Client()
        p.update(work_path + "\\server", revision_end)  # ���´���svn update.
        print ("���´���svn update")
    else:
        p = pysvn.Client()
        p.checkout(mysvn_url + "/server", work_path + "\\server")
        print ("serverĿ¼check out������")
        s = open('version.txt', 'w+')
        s.write(SVN_REVISION)
        s.close()

    # ����Դ��,�Ȱ� serverĿ¼check out������end
    print ("����Դ��,�Ȱ�serverĿ¼check out������end")

    # ��������Ҫ�����ļ���Ŀ¼�ṹ�������������д�����ű�begin
    # len(mysvn_url)����mysvn_urlL����
    # ��ȡ·����: os.path.dirname()
    # ��ȡ�ļ�����os.path.basename()
    # ������չ����os.path.splitext()

    os.system("svn diff --summarize -r %Start_version%:%SVN_REVISION% server>11.txt")

    newserver = work_path + "\\newserver"
    if os.path.exists(newserver):
        shutil.rmtree(newserver)
        os.mkdir(newserver)  # ��պ�������Ŀ¼
    else:
        os.makedirs(newserver)
    os.chdir(newserver)  # �л�������Ŀ¼newserver�¹���
    s = open(work_path + "\\11.txt")
    file_list = []
    for line in s.readlines():
        if re.match("A", line) or re.match("M", line):
            file_list.append(line)
            if os.path.exists(os.path.dirname(line[8:])):
                print (os.path.dirname(line[8:]) + "�Ѿ�����")
            else:
                print (os.path.dirname(line[8:]))
                os.makedirs(os.path.dirname(line[8:]))
    s.close()
    print ("#��������Ҫ�����ļ���Ŀ¼�ṹ�������������д�����ű�end")
    # ��������Ҫ�����ļ���Ŀ¼�ṹ�������������д�����ű�end

    # 2019-01-17 16:53:58
    # ͬһ�����ļ���ֻ����һ������Ĺ����У� ֻ���ļ����µ��ļ����������������
    # ����һ������ȫ��sql�ļ�����
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
    # ����������������ļ����µ�����sql�ļ�����increment_modify��increment_add�� ����ͬ����
    increment_modify = [  # �޸ĵ������ļ�
        "\\query\\querymenu.sql",
        "\\query\\query_add.sql",
        "\\dict\\",
        "\\init\\",
        "\\addorg\\"
    ]
    increment_add = [  # ���ӵ������ļ���
        "\\query\\querymenu.sql",
        "\\query\\query_add.sql",
        "\\dict\\",
        "\\init\\"
        # "\\addorg\\"
    ]
    # ������; table����ʽ��һ��
    special_table = ["\\table\\"]

    # �����⴦���ļ����ϸ��� "\\dir\\file" ���ļ��е���ײ��ļ�����ʽ��������������֧����Ϊ���޸ģ�ά������;
    # ƥ�䷽ʽ�Ǵ��ļ������Ƶ��ļ���summation��increment*���ܴ��ڰ�����ϵ������query\ ����query\querymenu.sql��
    # �������summation��increment���ؼ�飬���������queryȫ���ļ����������㲻ƥ��increment*����Ű�ȫ���ļ�����
    # �����𼶹��˵ķ�ʽ�� ��Ϊȫ���ļ����൥һ����򵥣���ɸѡ������ȫ���ļ�[query,proc,FISUPDATE,proc_opt,report,�ȵ�]��
    # �ٴ�����ͨ�����ļ���ɸѡ��[dict,init, addorg, �ȵ�]��
    # ֻʣ��δ���������ӵ�table�ļ���

    # ��ȡsql�ļ���ȱ�ٵı�������͸�ֵ
    define_init_variable = ["\\tradedb\\init\\sett_config.sql"]
    # ��ȡsql�ļ��� ȱ��ɾ���ؼ��ֵĵĴ����
    define_delete_variable = ["\\tradedb\\init\\init_pigeonhole.sql"]

    # ��¼ȫ���ļ�
    summation_file = [];
    # ��¼�޸��ļ�
    increment_modify_file = []
    # ��¼�����ļ�
    increment_add_file = []
    # ��¼special_table �ļ�
    special_table_modify_file = []
    special_table_add_file = []

    # ȫ���ļ�����begin
    os.chdir(newserver)  # �л�������Ŀ¼�¹���
    # ����ȫ��Ŀ¼ query,proc,FISUPDATE,proc_opt,report,stat,begin
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
        # ����summation�������
        if ".sql" in line and re.match("A", line) or ".sql" in line and re.match("M", line):
            for summation_member in summation:
                pos = line.find(summation_member)
                if pos >= 0:
                    available = 1

                    # ����increment* �������ȫ���ļ����°����������ļ�
                    for increment_member in increment_modify:
                        if line.find(increment_member) < 0:
                            continue  # δ���й���
                        # ���й���
                        increment_pos = increment_member.rfind(".sql")  # �������β׺��
                        if increment_pos == -1:  # increment �������У������������ļ���ֻ���ļ���
                            continue
                        summation_pos = summation_member.rfind(".sql")
                        if summation_pos == -1 and increment_pos >= 0:
                            available = 0  # increment �������У���summation�е������ļ�
                            break  # ������increment_member������
                        else:
                            available = 0
                            print ("�����ص����������")
                            print ("summation : " + summation_member)
                            print ("increment_modify : " + increment_member)
                            break

                    if 1 == available:
                        for increment_member in increment_add:
                            if line.find(increment_member) < 0:
                                continue  # δ���й���
                            # ���й���
                            increment_pos = increment_member.rfind(".sql")  # �������β׺��
                            if increment_pos == -1:  # increment �������У������������ļ���ֻ���ļ���
                                continue
                            summation_pos = summation_member.rfind(".sql")
                            if summation_pos == -1 and increment_pos >= 0:
                                available = 0  # increment �������У���summation�е������ļ�
                                break  # ������increment_member������
                            else:
                                available = 0
                                print ("�����ص����������")
                                print ("summation : " + summation_member)
                                print ("increment_modify : " + increment_member)
                                break

                    if 1 == available:
                        for special_member in special_table:
                            if line.find(special_member) < 0:
                                continue  # δ���й���
                            # ���й���
                            increment_pos = special_member.rfind(".sql")  # �������β׺��
                            if increment_pos == -1:  # increment �������У������������ļ���ֻ���ļ���
                                continue
                            summation_pos = summation_member.rfind(".sql")
                            if summation_pos == -1 and increment_pos >= 0:
                                available = 0  # increment �������У���summation�е������ļ�
                                break  # ������increment_member������
                            else:
                                available = 0
                                print ("�����ص����������")
                                print ("summation : " + summation_member)
                                print ("increment_modify : " + special_member)
                                break
                    # ����ȫ���ļ��������Ҳ��������ļ��У���ȫ������
                    if 1 == available:
                        break

            if 1 == available:
                # ԭ������Ϊ��һ��line�ĺ�����˸��س���.#ȥ���س���(\r)�����з�(\n)��ˮƽ�Ʊ��(\t)����ֱ�Ʊ��(\v)����ҳ��(\f)��
                svnurlfile = ''.join(line[8:].split())
                # ��print (svnurlfile)
                fp1 = os.path.dirname(svnurlfile)  # �ļ����ڵ���һ��Ŀ¼
                fp2 = svnurlfile.replace('\\', '/')
                svnurl1 = mysvn_url + "/" + fp2
                svnurl = unicode(svnurl1, 'GB2312')  # ת����svnʶ����룬��Ҫ��Ϊ����ʶ�����ĵ�svn����
                localpath1 = newserver + "\\" + fp1
                localpath = unicode(localpath1, 'GB2312')
                # print ("fp1:")
                # print (fp1)
                # print ("svnurl:")
                # print (svnurl)
                # print (localpath)

                p.export(svnurl, localpath, force=True)
                # ���� ��Чbat �� sql �Ľű�
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
                copy_file_list.remove(line)  # �ڸ������Ƴ�ɸѡ�����ļ�

    # ����ȫ��Ŀ¼ query,proc,FISUPDATE,proc_opt,report,stat,end
    file_list = list(copy_file_list)  # ȥ���Ѵ�����ļ�
    print ("����ȫ��Ŀ¼ query,proc,FISUPDATE,proc_opt,report,stat,end")

    # ��������Ŀ¼ query��querymenu.sql,dict,init, addorg , begin
    os.chdir(work_path)
    copy_file_list = list(file_list)  # ��������
    for line in file_list:
        available = 0
        if ".sql" in line and re.match("M", line):
            for increment_member in increment_modify:
                pos = line.find(increment_member)
                if pos >= 0:
                    available = 1
                    # ȥ�� special_table�ж���� �ļ���
                    for special_member in special_table:
                        if line.find(special_member) < 0:
                            continue  # δ���й���
                        # ���й���
                        increment_pos = special_member.rfind(".sql")  # �������β׺��
                        if increment_pos == -1:  # increment �������У������������ļ���ֻ���ļ���
                            continue
                        summation_pos = increment_member.rfind(".sql")
                        if summation_pos == -1 and increment_pos >= 0:
                            available = 0  # special_table�������У���increment�е������ļ�
                            break  # ������special_table������
                        else:
                            available = 0
                            print ("�����ص����������")
                            print ("summation : " + increment_member)
                            print ("increment_modify : " + special_member)
                            break
                    # ����increment_modify ���� �� ���� special__table�� �� ����ͨ�޸ĵ������ļ�����
                    if 1 == available:
                        break

            if 1 == available:
                svnurlfile = ''.join(line[8:].split())  # ȥ���س���(\r)�����з�(\n)��ˮƽ�Ʊ��(\t)����ֱ�Ʊ��(\v)����ҳ��(\f)��
                # print (svnurlfile)  # ��������print����Ϊ�˷��㿴��־
                fp1 = os.path.dirname(svnurlfile)
                fp2 = svnurlfile.replace('\\', '/')
                svnurl1 = mysvn_url + "/" + fp2
                svnurl = unicode(svnurl1, 'GB2312')  # ת����svnʶ����룬��Ҫ��Ϊ����ʶ�����ĵ�svn����
                filename = os.path.basename(svnurlfile)
                diff_test = p.diff_peg('', svnurl, peg_revision, revision_start, revision_end,
                                       diff_options=['-b', '-w'], diff_deleted=False,
                                       diff_added=True)  # �汾֮���ļ��Ĳ���,�������пո�,�հ׵ı仯��
                f = open('media.txt', 'wb+')
                # media.txt��һ�����ݻ�仯���ļ�,������д��diff_test���ٶ�ȡÿһ�е�����,�Զ����Ʒ�ʽд�룬��֤����sql�ļ���doc/windows,GB2312��ʽ
                f.write(diff_test)
                # �Ѳ�������д��media.txt��media������˼Ϊ���ʵ���˼,��˼�ǰ��ļ�һ��һ����˳��ش����������һ�����ֵ���һ���ļ�������media.txt������ֻ�����������һ���ļ�������
                f.close()  # �ر��ļ������д�붯��

                C = p.cat(svnurl, revision_end, peg_revision)
                f1 = open('media1.txt', 'wb+')
                f1.write(C)
                f1.close()
                f1 = open('media1.txt', 'rb')  # ����ر��ļ�����ܶ�ȡ�ļ�
                my_local_path = newserver + "\\" + svnurlfile
                f2 = open(my_local_path, 'wb+')  # �����ļ�
                L = set()
                for i in f1.readlines():  # ֻҪһ��use
                    if re.match("^use ", i):  # ֻ��ÿһ�еĿ�ʼƥ���ַ���use,match����ֻƥ�俪ͷ���ַ�
                        if i.split()[0] not in L:
                            f2.writelines(i.split()[0] + " " + i.split()[1])
                            L.add(i.split()[0])

                f1.close()
                f2.write("\r\n")
                # f2.write("go\r\n")
                f2.close()
                f2 = open(my_local_path, 'a')  # ��������
                # f2.write("go\n")  # ���з�\n����Ҫ,�����ǻ��к���д������,����go����һ����ܻ�ͬ��
                f = open('media.txt', 'r')  # ����ر��ļ�����ܶ�ȡ�ļ�
                for line1 in f.readlines():
                    if re.match("\+", line1) and not re.match("\+\+\+", line1) \
                            and not re.match("\+ {0,}--", line1) and not re.match("\+use", line1):
                        # ֻ��+��ɸѡ��������+++��@@,+--��ע��sql����䣩���˵�,\+��\Ϊת���ַ�,match����ֻƥ�俪ͷ���ַ�,����Ҳ������re.search("^+",line1),re.search("\A\+",line1),^+����\A\+����ʾ��ͷƥ�䡣
                        # print (line1)
                        f2.write(line1.lstrip("+"))
                        # �ѿ�ͷ�ġ�+��ȥ��;ѭ��д��һ���ļ����ٹر��ļ������ܲ�д��һ�о͹ر��ļ���Python�е�strip����ȥ���ַ�������β�ַ���ͬ��lstrip����ȥ����ߵ��ַ���rstrip����ȥ���ұߵ��ַ�
                f2.write("go\n")  # ����һ��go
                f2.close()  # ѭ��д��һ���ļ����ٹر��ļ�

                # ���� ��Чbat �� sql �Ľű�
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
                    # ȥ�� special_table�ж���� �ļ���
                    for special_member in special_table:
                        if line.find(special_member) < 0:
                            continue  # δ���й���
                        # ���й���
                        increment_pos = special_member.rfind(".sql")  # �������β׺��
                        if increment_pos == -1:  # increment �������У������������ļ���ֻ���ļ���
                            continue
                        summation_pos = increment_member.rfind(".sql")
                        if summation_pos == -1 and increment_pos >= 0:
                            available = 0  # special_table�������У���increment �е������ļ�
                            break  # ������special_table������
                        else:
                            available = 0
                            print ("�����ص����������")
                            print ("summation : " + increment_member)
                            print ("increment_modify : " + special_member)
                            break
                    # ����increment_add ���� �� ���� special__table�� �� ����ͨ�޸ĵ������ļ�����
                    if 1 == available:
                        break

            if 1 == available:
                svnurlfile = ''.join(line[8:].split())  # ȥ���س���(\r)�����з�(\n)��ˮƽ�Ʊ��(\t)����ֱ�Ʊ��(\v)����ҳ��(\f)��
                # print (svnurlfile)  # ��������print����Ϊ�˷��㿴��־
                fp1 = os.path.dirname(svnurlfile)
                fp2 = svnurlfile.replace('\\', '/')
                svnurl1 = mysvn_url + "/" + fp2
                svnurl = unicode(svnurl1, 'GB2312')  # ת����svnʶ����룬��Ҫ��Ϊ����ʶ�����ĵ�svn����
                localpath1 = newserver + "\\" + fp1
                localpath = unicode(localpath1, 'GB2312')
                # print ("fp1:")
                # print (fp1)
                # print ("svnurl:")
                # print (svnurl)
                # print (localpath)
                p.export(svnurl, localpath, force=True)

                # ���� ��Чbat �� sql �Ľű�
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

        # �޸ġ����ӱ�����Ҫ��ȡ��������͸�ֵ���� # ��tradedb\initĿ¼�� �������������Ҳ�λ��Ч���գ����ļ���ȡ�������������
        # ��������Ǽ���ȡ��������͸�ֵ��δ���Ǹ����ӵ��������ﾳ
        if 1 == available and 0 == invalid_flag:
            server_source_file = work_path + "\\" + line[8:].split()[0]
            newserver_file = newserver + "\\" + line[8:].split()[0]
            for define_init_file in define_init_variable:
                if define_init_file in line:  # ָ���ļ�
                    f1 = open(server_source_file, 'rb')
                    f2 = open(newserver_file, 'r+')
                    old = f2.read()
                    f2.seek(0)  # �ļ�ָ�붨�嵽�ļ�ͷ��
                    for i in f1.readlines():  # ��ȡ���ļ�
                        if re.match("declare @", i) or re.match("select @", i):
                            # �������� �ԡ�declare @��  ��ͷ,Լ��������ֵ�ԡ�select @����ͷ
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
                        if sentence.find("\'select * from") >= 0:  # �� select * from��ͷ �ַ�����Ϊɾ������������
                            select_pigeonhole.append(i);
                    f1.close()

                    f2 = open(server_source_file, "rb")
                    pop_flag = 0
                    delete_block = []
                    result_block = []
                    for line_num, sentence in enumerate(f2):
                        if re.match("declare @", sentence) or re.match("select @", sentence):
                            # �������� �ԡ�declare @��  ��ͷ,Լ��������ֵ�ԡ�select @����ͷ
                            result_block.append(sentence)
                        else:
                            delete_block.append(sentence)

                        if re.match("delete", sentence):
                            # delete ��ʼλ��
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
                                "from sysconfig where serverid = @serverid") >= 0:  # ÿһ��delete ����λ��
                            result_block += list(delete_block)  # ��¼���
                            pop_flag = 0  # ״̬λ��ԭ
                            continue
                    f2.close()
                    f1 = open(newserver_file, 'wb')
                    for line in result_block:
                        f1.writelines(line)
                    f1.writelines("go")
                    f1.close()
                break
# ��������Ŀ¼ query��querymenu.sql,dict,init, addorg ,end
file_list = list(copy_file_list)

print ("��������Ŀ¼ query��querymenu.sql,dict,init,addorg ,end")

# ��������Ŀ¼ table begin
os.chdir(work_path)
# s = open(work_path + "\\11.txt", 'rb')
copy_file_list = list(file_list)
for line in file_list:  # �����line��ʾmysvn_url��ַ
    available = 0
    if ".sql" in line and re.match("M", line):
        for special_member in special_table:
            if special_member in line:
                available = 1
                break

        if 1 == available:
            svnurlfile = ''.join(line[8:].split())  # ȥ���س���(\r)�����з�(\n)��ˮƽ�Ʊ��(\t)����ֱ�Ʊ��(\v)����ҳ��(\f)��
            # print (svnurlfile)  # ����print����Ϊ�˷��㿴��־
            fp1 = os.path.dirname(svnurlfile)
            fp2 = svnurlfile.replace('\\', '/')
            svnurl1 = mysvn_url + "/" + fp2
            svnurl = unicode(svnurl1, 'GB2312')  # ת����svnʶ����룬��Ҫ��Ϊ����ʶ�����ĵ�svn����
            filename = os.path.basename(svnurlfile)  # Ŀ����sql�ű�����
            p = pysvn.Client()
            f = open(r"file.txt", "wb+")
            file_text = p.cat(svnurl, revision_end, peg_revision)  # ��Ŀ���sql�ű��������
            f.write(file_text)
            f.close()

            # �ҳ� table �� table ���к� begin����ÿһ�� table �Ŀ�ʼ���������

            x = open(r"file.txt", "rb")
            y = open(r"tables.txt", "w+")
            for num, line_1 in enumerate(x):  # ��һ���ɱ��������ݶ���(���б�Ԫ����ַ���)���Ϊһ���������У�ͬʱ�г����ݺ������±�
                if re.match("--====================", line_1):
                    y.write(str(num))
                    y.write("\n")
            y.close()

            # �ҳ� table �� table ���к� end

            # д�����һ�е��к� begin

            x = open(r"file.txt", "rb")
            y = open(r"tables.txt", "a")
            lastline = x.readlines()
            y.write(str(len(lastline)))
            y.close()

            # д�����һ�е��к� end

            # ɸѡ�� table �仯���� begin
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
            # ɸѡ�� table �仯���� end

            # ɸѡ���仯�������ڵı� begin

            # ����仯�е��к� begin
            y = open(r"tables.txt", "r")
            z = open(r"changelinelist.txt", "r")
            Y = list(y)
            N = 0
            while N < len(Y):
                I = ''.join(Y[N].split())  # �ѻ��з�ȥ��
                Y[N] = I
                N += 1
            # print (Y)
            Z = list(z)
            N = 0
            while N < len(Z):
                I = ''.join(Z[N].split())  # �ѻ��з�ȥ��
                Z[N] = I
                N += 1
            # print (Z)

            # ����仯�е��к� end

            # ÿһ�仯���е��кŸ�Ŀ���Ŀ�ʼ��������е��к����Ƚϣ����ҳ��仯�������ڵı� begin

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
                N = N - len(Y)  # ��N��ֵ��������Ϊ0��һֱ��M����
            # ÿһ�仯���е��кŸ�Ŀ���Ŀ�ʼ��������е��к����Ƚϣ����ҳ��仯�������ڵı� end

            # ɸѡ���仯�������ڵı� end

            # ȥ���ظ�����ı� begin,��������ͬһ�� table ����仯��ֻ���һ�� table ��lineset=set()Ϊ�еļ���
            lineset = set()
            outfile = open(r"tablesout2.txt", "w+")
            for line_1 in open(r"tablesout.txt", "r"):
                if line_1 not in lineset:
                    outfile.write(line_1)
                    lineset.add(line_1)
            outfile.close()
            # ȥ���ظ����� end

            # ��ʼ���б仯�� table �� д�뵽Ŀ���ļ� begin

            f1 = open('file.txt', 'rb')  # ����ر��ļ�����ܶ�ȡ�ļ�
            f2 = open(newserver + "\\" + svnurlfile, 'wb+')  # �����ļ�
            L = set()
            for i in f1.readlines():  # ֻҪһ��use
                if re.match("use", i):  # ֻ��ÿһ�еĿ�ʼƥ���ַ���use,match����ֻƥ�俪ͷ���ַ�
                    if i.split()[0] not in L:
                        f2.writelines(i.split()[0] + " " + i.split()[1])
                        L.add(i.split()[0])
            f2.write("\r\n")
            # f2.write("go\r\n")
            f2.close()
            y = open(r"tablesout2.txt", "r")
            for i in y.readlines():
                # print (i)
                line1 = int(i.split()[0])  # �Կո�Ϊ�ָ����ȡ��һ���������к�
                line2 = int(i.split()[1])  # �Կո�Ϊ�ָ����ȡ�ڶ����������к�
                x = open(r"file.txt", "r")
                z = open(newserver + "\\" + svnurlfile, "a")
                for line_1 in x.readlines()[line1:line2]:
                    if not re.match(" {0,}--", line_1):
                        # print (line_1)
                        z.write(line_1)
            # z=open(newserver+"\\"+svnurlfile,"a")
            # z.write("go\n")
            z.close()
            # �������ӵ�sql�ļ�����ȥע��(/*����*/)����
            a = open(newserver + "\\" + svnurlfile, 'rb')
            b = a.read()
            c = open(newserver + "\\" + svnurlfile, 'wb')
            d = re.compile(" {0,}/\*.*?\*/", re.S)
            e = re.sub(d, "", b)
            c.write(e)
            c.close()
            a.close()
            # ��ʼ���б仯�� table �� д�뵽Ŀ���ļ� end

            # ���� ��Чbat �� sql �Ľű�
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
            svnurlfile = ''.join(line[8:].split())  # ȥ���س���(\r)�����з�(\n)��ˮƽ�Ʊ��(\t)����ֱ�Ʊ��(\v)����ҳ��(\f)��
            # print (svnurlfile)  # ��������print����Ϊ�˷��㿴��־
            fp1 = os.path.dirname(svnurlfile)
            fp2 = svnurlfile.replace('\\', '/')
            svnurl1 = mysvn_url + "/" + fp2
            svnurl = unicode(svnurl1, 'GB2312')  # ת����svnʶ����룬��Ҫ��Ϊ����ʶ�����ĵ�svn����
            localpath1 = newserver + "\\" + fp1
            localpath = unicode(localpath1, 'GB2312')
            # print ("fp1:")
            # print (fp1)
            # print ("svnurl:")
            # print (svnurl)
            # print (localpath)
            p.export(svnurl, localpath, force=True)
            # �������ӵ�sql�ļ�����ȥע��(/*����*/)����
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

            # ���� ��Чbat �� sql �Ľű�
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

# ��������Ŀ¼ table end
file_list = list(copy_file_list)
print ("��������Ŀ¼ table end")

# ��� ��ѡ������ȫ���ļ��������increment_summation
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
s.write("\n\nsummation_file ȫ���ļ�")
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
s.write("\n�ļ����� = " + str(total_counter))

s.write("\n\nincrement file �����ļ�")
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
s.write("\n�ļ����� = " + str(total_counter))

s.write("\n\nspecial_table ����\\table\\")
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
s.write("\n�ļ����� = " + str(total_counter))

# �����ļ��� ��Ч�ļ� invalid_file
counter = 0;
s.write("\n\n�����ļ�����Ч���ļ��� invalid file \n ")
summation_invalid_file.sort()
increment_invalid_file.sort()
special_table_invalid_file.sort()
invalid_file = summation_invalid_file + increment_invalid_file + special_table_invalid_file
for i in invalid_file:
    s.write(i)
counter = len(invalid_file)
total_counter += counter
s.write("\ninvalid file = " + str(counter))
s.write("\ntotal number ȫ���ļ����� = " + str(total_counter))

# ��� \6.7.9.0_0.1.0\newserver·���µĿ��ļ���
DelInvaildFolder(newserver)
s.writelines("\n\nɾ�����ļ���\n")
for delete_folder in delete_folder_list:
    s.writelines(delete_folder)
s.close()

s = open(increment_summation_txt, 'r')
for i in s.readlines():
    print i
s.close()

# ���� 11.txt �е���Ч�ļ�
s = open("11.txt", 'wb')
for i in copy_file_list_2:
    if i not in invalid_file:
        s.writelines(i)
s.close()

# ���������Ŀ¼������Ŀ¼ begin
if os.path.exists(PATCH_NAME + "\\server"):
    shutil.rmtree(PATCH_NAME + "\\server")
    shutil.rmtree(PATCH_NAME + "\\doc")
    os.makedirs(PATCH_NAME + "\\server")
    os.makedirs(PATCH_NAME + "\\doc")
else:
    os.makedirs(PATCH_NAME + "\\server")
    os.makedirs(PATCH_NAME + "\\doc")
# ���������Ŀ¼������Ŀ¼ end

# sqlsh.exe ����
os.chdir(work_path + "\\server\\tradedb")
if os.path.exists(work_path + "\\server\\tradedb\\sqlsh.exe"):
    shutil.copy(work_path + "\\server\\tradedb\\sqlsh.exe", work_path + "\\newserver\\server")
else:
    print(work_path + "\\server\\tradedb\\sqlsh.exe" + "������")
# PatchVer.sql ����
os.chdir(work_path + "\\newserver\\server")
a = open('PatchVer.sql', 'w+')
a.write('''exec nb_add_version \'''' + Sql_version + '''\'go''')
a.close()

# �����ű��ļ�����
# 01_���׷�����(run).bat begin
os.chdir(work_path + "\\newserver\\server")
# run˳���б��б��ص�֮һ����˳��ģ��Ժ�˳����ˣ����Ե�һ�������б��˳�򣬻������µ�Ŀ¼���ӣ������Ⱥ�˳�����б�����Ӽ��ɡ�
orderrunlist = ["tradedb\\table\\", "tradedb\\stat\\", "tradedb\\init\\", "tradedb\\dict\\", "tradedb\\query\\",
                "tradedb\\proc_opt\\", "tradedb\\proc\\", "tradedb\\FISUPDATE\\proc\\",
                "tradedb\\interface_vip\\table\\", "tradedb\\interface_vip\\init\\",
                "tradedb\\interface_vip\\dict\\", "tradedb\\interface_vip\\query\\",
                "tradedb\\interface_vip\\proc\\", "tradedb\\report\\", "tradedb\\DBCONTROL\\table\\",
                "tradedb\\DBCONTROL\\init\\", "tradedb\\DBCONTROL\\proc\\", "tradedb\\init\\datafix.sql"]
# Ŀ¼���ڣ���д��Q1_����.bat�ļ�����ЩĿ¼��д���ĸ�bat������ֲ�涨��Ϊ׼��
# �����ļ����ڲ����ȼ�˳��ͳһ���֧�����ȼ��Զ���,δ�������ȼ����ļ��������⴦��
file_order_list = ["TCrt", "proc"]
if os.path.exists(work_path + "\\newserver\\server\\tradedb"):
    b = open("01_���׷�����(run).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    ��һ��Win�� ������ȯ''' + Sql_version + '''������  ���׷�����(run).bat
@ECHO ------------------------------------------------------------------------
@ECHO Ϊ��֤����ִ�������ű���ע�����¼��㣺
@ECHO    1. ��ر����е����ݿ�����
@ECHO    2. ���������д����µı�,��ֹͣ������ݿ⸴��
@ECHO ========================================================================
pause
sqlsh -U���׿��û��� -P���׿����� -S���׿��������ַ -drun -i .\PatchVer.sql

''')
    b.close()
    # ��˳���б�orderrunlist�л�ȡ�������д��bat,������д�룬��������������ÿһ��˳���������ʹ��sort����������򣬷���ǰ�������汾�Ա�bat������˳����Ҳ��öԱȡ�
    for i in orderrunlist:
        print "\n======================================================================"
        print("run˳��" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("01_���׷�����(run).bat", "a")
        drun = ("noexist")
        lrun = []
        for line in a.readlines():
            if "server\\tradedb" in line and re.match("A", line) or "server\\tradedb" in line and re.match("M",
                                                                                                           line):
                if i in line:
                    lrun.append(line)

        # ��������ļ�����˳������
        run_list_in_order = [[] for i in range(len(file_order_list))]  # ��ά����ֱ��Ų�ͬ���ȼ����ļ�
        # ����δ�������ȼ����ļ�
        run_list_out_of_order = []
        print "���������ʼ��״̬ ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lrun ", lrun

        for subfile in lrun:
            exist_flag = 0
            pos = subfile.rfind("\\")  # ȡ�ļ���
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # ���������ȼ���¼�ļ�������run_list_in_order
                    break
            # δ�������ȼ��Ĵ�����һ������run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # ��ǰ�ļ����������ļ��������

        lrun = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lrun += run_list_in_order[cursor]  # �ϲ�����
        # δ�������ȼ����ļ���������������
        run_list_out_of_order.sort()
        print "δ�������ȼ� ", run_list_out_of_order
        lrun += run_list_out_of_order  # �ϲ�����
        print "�������"
        print lrun
        print "======================================================================\n"

        for i in lrun:
            c.write(re.sub(r"\r", "", i))
            drun = ("exist")
        if drun == ("exist"):  # ����д�淶����ÿһ��˳��������н��з��ࡣ
            c.write("\n")
    c = open("01_���׷�����(run).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("01_���׷�����(run).bat", "rb")
    f = c.read()
    c1 = open("01_���׷�����(run).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U���׿��û��� -P���׿����� -S���׿��������ַ -drun -i .\\", f)  # ������ֲ�淶��д��re.sub�ַ����Ҳ��滻����ϸ�ٶ�re.sub
    c1.write(q)
    c1.close()
    # ��ǰ���datafix.sqlȥ�� begin
    a = open("01_���׷�����(run).bat", "rb")
    b = []  # ����һ�����б��������Q1_����.batÿһ��
    for i in a.readlines():
        b.append(i)
    for i in b:
        if "datafix.sql" in i:
            I = i
            b.remove(I)  # removeֻȥ��ƥ�����һ��datafix.sql
            break  # ֻ��ǰ��һ��
    print(b)
    # ��ǰ���datafix.sqlȥ�� end
    c = open("01_���׷�����(run).bat", "wb")
    for i in b:
        c.write(i)
    c.close()
# 01_���׷�����(run).bat end
# 02_���׷�����(report).bat begin
os.chdir(work_path + "\\newserver\\server")
# run˳���б��б��ص�֮һ����˳��ģ��Ժ�˳����ˣ����Ե�һ�������б��˳�򣬻������µ�Ŀ¼���ӣ������Ⱥ�˳�����б�����Ӽ��ɡ�
orderrunlist = ["reportdb\\table\\", "reportdb\\proc\\"]
# Ŀ¼���ڣ���д��Q1_����.bat�ļ�����ЩĿ¼��д���ĸ�bat������ֲ�涨��Ϊ׼��
# �����ļ����ڲ����ȼ�˳��ͳһ���֧�����ȼ��Զ���,δ�������ȼ����ļ��������⴦��
file_order_list = ["TCrt", "proc"]
if os.path.exists(work_path + "\\newserver\\server\\reportdb"):
    b = open("02_���׷�����(report).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    ��һ��Win�� ������ȯ''' + Sql_version + '''������  ���׷�����(report).bat
@ECHO ------------------------------------------------------------------------
@ECHO Ϊ��֤����ִ�������ű���ע�����¼��㣺
@ECHO    1. ��ر����е����ݿ�����
@ECHO    2. ���������д����µı�,��ֹͣ������ݿ⸴��
@ECHO ========================================================================
pause

''')
    b.close()
    # ��˳���б�orderrunlist�л�ȡ�������д��bat,������д�룬��������������ÿһ��˳���������ʹ��sort����������򣬷���ǰ�������汾�Ա�bat������˳����Ҳ��öԱȡ�
    for i in orderrunlist:
        print "\n======================================================================"
        print("run˳��" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("02_���׷�����(report).bat", "a")
        drun = ("noexist")
        lrun = []
        for line in a.readlines():
            if "server\\reportdb" in line and re.match("A", line) or "server\\reportdb" in line and re.match("M",
                                                                                                             line):
                if i in line:
                    lrun.append(line)

        # ��������ļ�����˳������
        run_list_in_order = [[] for i in range(len(file_order_list))]  # ��ά����ֱ��Ų�ͬ���ȼ����ļ�
        # ����δ�������ȼ����ļ�
        run_list_out_of_order = []
        print "���������ʼ��״̬ ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lrun ", lrun

        for subfile in lrun:
            exist_flag = 0
            pos = subfile.rfind("\\")  # ȡ�ļ���
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # ���������ȼ���¼�ļ�������run_list_in_order
                    break
            # δ�������ȼ��Ĵ�����һ������run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # ��ǰ�ļ����������ļ��������

        lrun = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lrun += run_list_in_order[cursor]  # �ϲ�����
        # δ�������ȼ����ļ���������������
        run_list_out_of_order.sort()
        print "δ�������ȼ� ", run_list_out_of_order
        lrun += run_list_out_of_order  # �ϲ�����
        print "�������"
        print lrun
        print "======================================================================\n"

        for i in lrun:
            c.write(re.sub(r"\r", "", i))
            drun = ("exist")
        if drun == ("exist"):  # ����д�淶����ÿһ��˳��������н��з��ࡣ
            c.write("\n")
    c = open("02_���׷�����(report).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("02_���׷�����(report).bat", "rb")
    f = c.read()
    c1 = open("02_���׷�����(report).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U���׿��û��� -P���׿����� -S���׿��������ַ -dreport -i .\\", f)  # ������ֲ�淶��д��re.sub�ַ����Ҳ��滻����ϸ�ٶ�re.sub
    c1.write(q)
    c1.close()
# 02_���׷�����(report).bat end
# 03_��ط�����(run).bat begin
os.chdir(work_path + "\\newserver\\server")
# ���run˳���б��б��ص�֮һ����˳��ģ��Ժ�˳����ˣ����Ե�һ�������б��˳�򣬻������µ�Ŀ¼���ӣ������Ⱥ�˳�����б�����Ӽ��ɡ�
orderfkrunlist = ["tradedb\\table\\", "tradedb\\stat\\", "tradedb\\init\\", "tradedb\\dict\\", "tradedb\\query\\",
                  "tradedb\\proc_opt\\", "tradedb\\proc\\", "tradedb\\FISUPDATE\\proc\\",
                  "tradedb\\interface_vip\\table\\", "tradedb\\interface_vip\\init\\",
                  "tradedb\\interface_vip\\dict\\", "tradedb\\interface_vip\\query\\",
                  "tradedb\\interface_vip\\proc\\", "tradedb\\report\\", "tradedb\\DBCONTROL\\table\\",
                  "tradedb\\DBCONTROL\\init\\", "tradedb\\DBCONTROL\\proc\\"]
# Ŀ¼���ڣ���д��Q1_���.bat�ļ�����ЩĿ¼��д���ĸ�bat������ֲ�涨��Ϊ׼��

# �����ļ����ڲ����ȼ�˳��ͳһ���֧�����ȼ��Զ���,δ�������ȼ����ļ��������⴦��
file_order_list = ["TCrt", "proc"]

if os.path.exists(work_path + "\\newserver\\server\\tradedb"):
    b = open("03_��ط�����(run).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    ��һ��Win�� ������ȯ''' + Sql_version + '''������  ��ط�����(run).bat
@ECHO ------------------------------------------------------------------------
@ECHO Ϊ��֤����ִ�������ű���ע�����¼��㣺
@ECHO    1. ��ر����е����ݿ�����
@ECHO    2. ���������д����µı�,��ֹͣ������ݿ⸴��
@ECHO ========================================================================
pause
sqlsh -U��ؿ��û��� -P��ؿ����� -S��ؿ��������ַ -drun -i .\PatchVer.sql

''')
    b.close()
    # ��˳���б�orderfkrunlist�л�ȡ�������д��bat,������д�룬��������������ÿһ��˳���������ʹ��sort����������򣬷���ǰ�������汾�Ա�bat������˳����Ҳ��öԱȡ�
    for i in orderfkrunlist:
        print "\n======================================================================"
        print("fkrun˳��" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("03_��ط�����(run).bat", "a")
        dfkrun = ("noexist")
        lfkrun = []
        for line in a.readlines():
            if "server\\tradedb" in line and re.match("A", line) or "server\\tradedb" in line and re.match("M",
                                                                                                           line):
                if i in line:
                    lfkrun.append(line)

                # ��������ļ�����˳������
        run_list_in_order = [[] for i in range(len(file_order_list))]  # ��ά����ֱ��Ų�ͬ���ȼ����ļ�
        # ����δ�������ȼ����ļ�
        run_list_out_of_order = []
        print "���������ʼ��״̬ ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lfkrun ", lfkrun

        for subfile in lfkrun:
            exist_flag = 0
            pos = subfile.rfind("\\")  # ȡ�ļ���
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # ���������ȼ���¼�ļ�������run_list_in_order
                    break
            # δ�������ȼ��Ĵ�����һ������run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # ��ǰ�ļ����������ļ��������

        lfkrun = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lfkrun += run_list_in_order[cursor]  # �ϲ�����
        # δ�������ȼ����ļ���������������
        run_list_out_of_order.sort()
        print "δ�������ȼ� ", run_list_out_of_order
        lfkrun += run_list_out_of_order  # �ϲ�����
        print "�������"
        print lfkrun
        print "======================================================================\n"

        for i in lfkrun:
            c.write(re.sub(r"\r", "", i))
            dfkrun = ("exist")
        if dfkrun == ("exist"):  # ����д�淶����ÿһ��˳��������н��з��ࡣ
            c.write("\n")
    c = open("03_��ط�����(run).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("03_��ط�����(run).bat", "rb")
    f = c.read()
    c1 = open("03_��ط�����(run).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U��ؿ��û��� -P��ؿ����� -S��ؿ��������ַ -drun -i .\\", f)  # ������ֲ�淶��д��re.sub�ַ����Ҳ��滻����ϸ�ٶ�re.sub
    c1.write(q)
    c1.close()
    # ��ǰ���datafix.sqlȥ�� �Ѻ����datafix_riskdb.sql begin
    a = open("03_��ط�����(run).bat", "rb")
    b = []  # ����һ�����б��������Q1_���.batÿһ��
    for i in a.readlines():
        b.append(i)
    for i in b:
        if "datafix.sql" in i:
            print("I0:" + i)
            I0 = i
            b.remove(I0)  # removeֻȥ��ƥ�����һ��datafix.sql
            break  # ֻ��ǰ��һ��
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
    # ��ǰ���datafix.sqlȥ�� �Ѻ����datafix_riskdb.sql begin end
    c = open("03_��ط�����(run).bat", "wb")
    for i in b:
        c.write(i)
        print(i)
    c.close()
# 03_��ط�����(run).bat end
# 04_��ط�����(riskdb).bat begin
os.chdir(work_path + "\\newserver\\server")
# ���run˳���б��б��ص�֮һ����˳��ģ��Ժ�˳����ˣ����Ե�һ�������б��˳�򣬻������µ�Ŀ¼���ӣ������Ⱥ�˳�����б�����Ӽ��ɡ�
orderfkrunlist = ["riskdb\\init\\datafix_riskdb.sql", "riskdb\\table\\", "riskdb\\init\\", "riskdb\\proc\\"]
# Ŀ¼���ڣ���д��04_��ط�����(riskdb).bat�ļ�����ЩĿ¼��д���ĸ�bat������ֲ�涨��Ϊ׼��

# �����ļ����ڲ����ȼ�˳��ͳһ���֧�����ȼ��Զ���,δ�������ȼ����ļ��������⴦��
file_order_list = ["TCrt", "proc"]

if os.path.exists(work_path + "\\newserver\\server\\riskdb"):
    b = open("04_��ط�����(riskdb).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    ��һ��Win�� ������ȯ''' + Sql_version + '''������  ��ط�����(riskdb).bat
@ECHO ------------------------------------------------------------------------
@ECHO Ϊ��֤����ִ�������ű���ע�����¼��㣺
@ECHO    1. ��ر����е����ݿ�����
@ECHO    2. ���������д����µı�,��ֹͣ������ݿ⸴��
@ECHO ========================================================================
pause

''')
    b.close()
    # ��˳���б�orderfkrunlist�л�ȡ�������д��bat,������д�룬��������������ÿһ��˳���������ʹ��sort����������򣬷���ǰ�������汾�Ա�bat������˳����Ҳ��öԱȡ�
    for i in orderfkrunlist:
        print "\n======================================================================"
        print("fkrun˳��" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("04_��ط�����(riskdb).bat", "a")
        dfkrun = ("noexist")
        lfkrun = []
        for line in a.readlines():
            if "server\\riskdb" in line and re.match("A", line) or "server\\riskdb" in line and re.match("M", line):
                if i in line:
                    lfkrun.append(line)

            # ��������ļ�����˳������
        run_list_in_order = [[] for i in range(len(file_order_list))]  # ��ά����ֱ��Ų�ͬ���ȼ����ļ�
        # ����δ�������ȼ����ļ�
        run_list_out_of_order = []
        print "���������ʼ��״̬ ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lfkrun ", lfkrun

        for subfile in lfkrun:
            exist_flag = 0
            pos = subfile.rfind("\\")  # ȡ�ļ���
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # ���������ȼ���¼�ļ�������run_list_in_order
                    break
            # δ�������ȼ��Ĵ�����һ������run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # ��ǰ�ļ����������ļ��������

        lfkrun = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lfkrun += run_list_in_order[cursor]  # �ϲ�����
        # δ�������ȼ����ļ���������������
        run_list_out_of_order.sort()
        print "δ�������ȼ� ", run_list_out_of_order
        lfkrun += run_list_out_of_order  # �ϲ�����
        print "�������"
        print lfkrun
        print "======================================================================\n"

        for i in lfkrun:
            c.write(re.sub(r"\r", "", i))
            dfkrun = ("exist")
        if dfkrun == ("exist"):  # ����д�淶����ÿһ��˳��������н��з��ࡣ
            c.write("\n")
    c = open("04_��ط�����(riskdb).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("04_��ط�����(riskdb).bat", "rb")
    f = c.read()
    c1 = open("04_��ط�����(riskdb).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U��ؿ��û��� -P��ؿ����� -S��ؿ��������ַ -driskdb -i .\\", f)  # ������ֲ�淶��д��re.sub�ַ����Ҳ��滻����ϸ�ٶ�re.sub
    c1.write(q)
    c1.close()
    # ��ǰ���datafix.sqlȥ�� �Ѻ����datafix_riskdb.sql begin
    a = open("04_��ط�����(riskdb).bat", "rb")
    b = []  # ����һ�����б��������Q1_���.batÿһ��
    for i in a.readlines():
        b.append(i)
    for i in b:
        if "datafix.sql" in i:
            print("I0:" + i)
            I0 = i
            b.remove(I0)  # removeֻȥ��ƥ�����һ��datafix.sql
            break  # ֻ��ǰ��һ��
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
    # ��ǰ���datafix.sqlȥ�� �Ѻ����datafix_riskdb.sql begin end
    c = open("04_��ط�����(riskdb).bat", "wb")
    for i in b:
        c.write(i)
        print(i)
    c.close()
# 04_��ط�����(riskdb).bat end
# 05_��ʷ������(run).bat begin
# his˳���б� begin
orderhislist = ["\\TCrt_rundbProc.sql", "\\Thist_run.sql", "\\THist_run_credit.sql", "\\THist_run_openfund.sql"]
# �����ļ����ڲ����ȼ�˳��ͳһ���֧�����ȼ��Զ���,δ�������ȼ����ļ��������⴦��
file_order_list = ["TCrt", "proc"]

if os.path.exists(work_path + "\\newserver\\server\\querydb"):
    b = open("05_��ʷ������(run).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    ��һ��Win�� ������ȯ''' + Sql_version + '''������  ��ʷ������(run).bat
@ECHO ------------------------------------------------------------------------
@ECHO Ϊ��֤����ִ�������ű���ע�����¼��㣺
@ECHO    1. ��ر����е����ݿ�����
@ECHO    2. ���������д����µı�,��ֹͣ������ݿ⸴��
@ECHO ========================================================================
pause
''')
    b.close()
    for i in orderhislist:
        print "\n======================================================================"
        print("his˳��" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("05_��ʷ������(run).bat", "a")
        dhis = ("noexist")
        lhis = []
        for line in a.readlines():
            if "server\\querydb" in line and re.match("A", line) or "server\\querydb" in line and re.match("M",
                                                                                                           line):
                if i in line:
                    lhis.append(line)

        # ��������ļ�����˳������
        run_list_in_order = [[] for i in range(len(file_order_list))]  # ��ά����ֱ��Ų�ͬ���ȼ����ļ�
        # ����δ�������ȼ����ļ�
        run_list_out_of_order = []
        print "���������ʼ��״̬ ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lhis ", lhis

        for subfile in lhis:
            exist_flag = 0
            pos = subfile.rfind("\\")  # ȡ�ļ���
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # ���������ȼ���¼�ļ�������run_list_in_order
                    break
            # δ�������ȼ��Ĵ�����һ������run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # ��ǰ�ļ����������ļ��������

        lhis = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lhis += run_list_in_order[cursor]  # �ϲ�����
        # δ�������ȼ����ļ���������������
        run_list_out_of_order.sort()
        print "δ�������ȼ� ", run_list_out_of_order
        lhis += run_list_out_of_order  # �ϲ�����
        print "�������"
        print lhis
        print "======================================================================\n"

        for i in lhis:
            c.write(re.sub(r"\r", "", i))
            dhis = ("exist")
        if dhis == ("exist"):
            c.write("\n")
    c = open("05_��ʷ������(run).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("05_��ʷ������(run).bat", "rb")
    f = c.read()
    c1 = open("05_��ʷ������(run).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U��ʷ���û��� -P��ʷ������ -S��ʷ���������ַ -drun -i .\\", f)
    print(q)
    c1.write(q)
    c1.close()
    # 05_��ʷ������(run).bat end
# 06_��ʷ������(his).bat begin
# his˳���б� begin
orderhislist = ["querydb\\hisdb\\table\\", "querydb\\hisdb\\init\\", "querydb\\hisdb\\FISUPDATE\\proc\\"]

# �����ļ����ڲ����ȼ�˳��ͳһ���֧�����ȼ��Զ���,δ�������ȼ����ļ��������⴦��
file_order_list = ["TCrt", "proc"]

if os.path.exists(work_path + "\\newserver\\server\\querydb"):
    b = open("06_��ʷ������(his).bat", "w+")
    b.write('''@ECHO ========================================================================
@ECHO    ��һ��Win�� ������ȯ''' + Sql_version + '''������  ��ʷ������(his).bat
@ECHO ------------------------------------------------------------------------
@ECHO Ϊ��֤����ִ�������ű���ע�����¼��㣺
@ECHO    1. ��ر����е����ݿ�����
@ECHO    2. ���������д����µı�,��ֹͣ������ݿ⸴��
@ECHO ========================================================================
pause
''')
    b.close()
    for i in orderhislist:
        print "\n======================================================================"
        print("his˳��" + i)
        a = open(work_path + "\\11.txt", 'rb')
        c = open("06_��ʷ������(his).bat", "a")
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

        # ��������ļ�����˳������
        run_list_in_order = [[] for i in range(len(file_order_list))]  # ��ά����ֱ��Ų�ͬ���ȼ����ļ�
        # ����δ�������ȼ����ļ�
        run_list_out_of_order = []
        print "���������ʼ��״̬ ", run_list_in_order
        # print "len(run_list_in_order) ", len(run_list_in_order)
        # print "len(file_order_list) ", len(file_order_list)
        print "lhis ", lhis

        for subfile in lhis:
            exist_flag = 0
            pos = subfile.rfind("\\")  # ȡ�ļ���
            subfilename = subfile[pos:]
            cursor = -1
            # print subfilename
            for priority in file_order_list:
                cursor += 1
                if subfilename.find(priority) >= 0:
                    exist_flag = 1
                    run_list_in_order[cursor].append(subfile)
                    # ���������ȼ���¼�ļ�������run_list_in_order
                    break
            # δ�������ȼ��Ĵ�����һ������run_list_out_of_order
            if exist_flag == 0:
                run_list_out_of_order.append(subfile)
        # ��ǰ�ļ����������ļ��������

        lhis = []
        cursor = 0
        for cursor in range(len(file_order_list)):
            run_list_in_order[cursor].sort()
            print "priority ", file_order_list[cursor]
            print run_list_in_order[cursor]
            lhis += run_list_in_order[cursor]  # �ϲ�����
        # δ�������ȼ����ļ���������������
        run_list_out_of_order.sort()
        print "δ�������ȼ� ", run_list_out_of_order
        lhis += run_list_out_of_order  # �ϲ�����
        print "�������"
        print lhis
        print "======================================================================\n"

        for i in lhis:
            c.write(re.sub(r"\r", "", i))
            dhis = ("exist")
        if dhis == ("exist"):
            c.write("\n")
    c = open("06_��ʷ������(his).bat", "a")
    c.write("pause\n")
    c.close()
    a.close()
    c = open("06_��ʷ������(his).bat", "rb")
    f = c.read()
    c1 = open("06_��ʷ������(his).bat", "wb")
    p = re.compile(".*server\\\\", re.M)
    q = re.sub(p, r"sqlsh -U��ʷ���û��� -P��ʷ������ -S��ʷ���������ַ -dhis -i .\\", f)
    print(q)
    c1.write(q)
    c1.close()
    # 06_��ʷ������(his).bat end
