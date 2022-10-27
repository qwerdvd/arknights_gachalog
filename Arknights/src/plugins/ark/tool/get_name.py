import os
import re

# raw = {'Name': '', 'Chinese_name': '', 'image_name': ['', '']}
# raw = {'Name': '', 'Chinese_name': ''}

f = open("C:\\Users\\qwerdvd\\Desktop\\1\\新建文件夹\\新文件 2.txt", "r")
lines = f.readlines()

for line in lines:
    raw = {'Name': '', 'Chinese_name': ''}
    raw['Name'] = line
    raw['Chinese_name'] = line
    # result.append[raw]

    pattern = re.findall(r"\d+_(.+).png", line)

