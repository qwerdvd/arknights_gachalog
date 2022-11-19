import re

str = "surtr_t_2[withdraw].interval"
str1 = str.split("[")
str2 = str1[1].split("]")
print(re.split("[\[\]\.]", str))
print(str2)
