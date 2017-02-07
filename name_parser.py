#!/usr/bin/env python3

import os
import re
import sys, shelve

# 文件名解析函数
def parse_name(name, path):
    filter_list = {'Chinese','DL版','中国翻訳','complete','无修正','中文','Digital','英译中','無修正','已扫版','自购'}
    tmp = name
    name = name.strip()
    data_list = []

    while len(name) > 0:
        for i in range(len(name)):
            if name[i] == '(' or name[i] == '[':
                if i != 0:
                    data_list.append([name[:i].strip(), 0])
                if name[i] == '(':
                    index = name.index(')')
                    text = name[i+1:index].strip()
                    data_list.append([text,1])
                else:
                    index = name.index(']')
                    text = name[i+1:index].strip()
                    if text not in filter_list:
                        data_list.append([text, 2])

                name = name[index+1:].strip()
                break
        else:
            data_list.append([name.strip(), 0])
            break

    return [tmp, data_list, path]


class info(object):
    def __init__(self, origin_filename, name, producer, author, source, Chinesize, origin, path):
        self.origin_filename = origin_filename
        self.name = name
        self.producer = producer
        self.author = author
        self.source = source
        self.Chinesize = Chinesize
        self.origin = origin
        self.path = path




base_dir = 'G:\\ACG\\Comic\\note\\comic' # 根目录
name_list = os.listdir(base_dir) # 读取文件树
name_list.sort() # 进行排序使肉眼观察更加方便
name_list = [[x, os.path.join(base_dir, x)] for x in name_list]

parsed_name_list = []
error_name_list = []


# 将方括号标准化
lsb = re.compile('【')
rsb = re.compile('】')
for i in range(len(name_list)):
    name_list[i][0], num = lsb.subn('[', name_list[i][0])
    name_list[i][0], num = rsb.subn(']', name_list[i][0])

lcb = re.compile('（')
rcb = re.compile('）')
for i in range(len(name_list)):
    name_list[i][0], num = lcb.subn('(', name_list[i][0])
    name_list[i][0], num = rcb.subn(')', name_list[i][0])

# 筛选文件名
good_naming = []
bad_naming = [] # 坏命名只能人工处理

regex = re.compile('[\(\)\[\]]')
for i in range(len(name_list)):
    if re.search(regex, name_list[i][0]) and re.match(regex, name_list[i][0]):
        good_naming.append(name_list[i])
    else:
        bad_naming.append(name_list[i])

# 初步检查括号不匹配现象
lsb = re.compile('\[')
rsb = re.compile('\]')
lcb = re.compile('\(')
rcb = re.compile('\)')

delete_index = []
for i in range(len(name_list)):
    lsb_num = len(re.findall(lsb, name_list[i][0]))
    rsb_num = len(re.findall(rsb, name_list[i][0]))
    lcb_num = len(re.findall(lcb, name_list[i][0]))
    rcb_num = len(re.findall(rcb, name_list[i][0]))

    if lsb_num - rsb_num != 0 or lcb_num - rcb_num != 0:
        delete_index.append(i)
        error_name_list.append(name_list[i])

for index in delete_index[::-1]:
    name_list.pop(index)


# 文件名解析
parse_list = []
for name in good_naming:
    try:
        parse_list.append(parse_name(name[0], name[1]))
    except:
        error_name_list.append((name))

# 二次解析
info_list = []
error_zero = []
remain_two_count = {}
remain_two = []
for item in parse_list:
    error = []
    origin_name = item[0]
    detail_list = item[1]
    file_path = item[2]

    print(detail_list)
    try:
        key = ''.join([__builtins__.str(x[1]) for x in detail_list])
        if key.count('0') > 1:
            for i in range(len(key)):
                if key[i] == '0':
                    error.append(detail_list[i][0])
        elif key.count('0') == 1:
            zero_index = key.index('0')
            one_index = [index for index in range(len(key)) if key[index] == '1']
            two_index = [index for index in range(len(key)) if key[index] == '2']

            name = detail_list[zero_index][0]

            if zero_index + 1 < len(detail_list) and detail_list[zero_index+1][1] == 1:
                origin = detail_list[zero_index+1][0]
                one_index.remove(zero_index+1)
            else:
                origin = None

            # 圆括号中的一般为原作名或来源
            source = None
            if len(one_index) > 0:
                source_index = one_index.pop(0)
                source = detail_list[source_index][0]

            for i in range(len(one_index)):
                error.append(detail_list[i][0])


            Chinesize = None
            for index in two_index:
                if '汉化' in detail_list[index][0] or '漢化' in detail_list[index][0] or '中字' in detail_list[index][0] or '组' in detail_list[index][0]:
                    Chinesize = detail_list[index][0]
                    two_index.remove(index)
                    break

            author = None
            producer = None
            if len(two_index) > 0:
                to_be_author_list = []
                for i in two_index:
                    if '(' in detail_list[i][0]:
                        to_be_author_list.append(i)
                if len(to_be_author_list) > 0:
                    author_index = to_be_author_list[0]
                    left_b = detail_list[author_index][0].index('(')
                    right_b = detail_list[author_index][0].index(')')
                    author = detail_list[author_index][0][left_b+1:right_b]
                    producer = detail_list[author_index][0][:left_b]
                    two_index.remove(author_index)
                else:
                    author_index = two_index[0]
                    author = detail_list[author_index][0]
                    two_index.remove(author_index)

            if len(two_index) > 0:
                if not Chinesize:
                    regex = re.compile('^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]+$')
                    for i in two_index:
                        if re.match(regex, detail_list[i][0]):
                            continue
                        else:
                            Chinesize = detail_list[i][0]
                            two_index.remove(i)
                            break

            if len(two_index) > 0:
                if len(two_index) not in remain_two_count:
                    remain_two_count[len(two_index)] = 0
                remain_two_count[len(two_index)] += 1
                remain_two.append([origin_name, [detail_list[i][0] for i in two_index]])

            new_info = info(origin_name, name, producer, author, source, Chinesize, origin, file_path)
            parsed_name_list.append(new_info)

            print(origin_name)
            print('name', name)
            print('origin', origin)
            print('author', author)
            print('producer',producer)
            print('Chinesize', Chinesize)
            print('source', source)
            print('error', error)
            print('-------------------------')
        else:
            error_name_list.append([origin_name,file_path])
    except:
        error_name_list.append([origin_name,file_path])


file = shelve.open("E:\\info.dat")
file['name_list'] = name_list
file['error_name_list'] = error_name_list
file['parsed_name_list'] = parsed_name_list
file['bad_naming'] = bad_naming
file.close()


# file = shelve.open("E:\\info.dat")
# parsed_name_list = file['parsed_name_list']
