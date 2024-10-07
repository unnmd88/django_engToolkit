import re

name_val = '   D M    vssvdsdsd   vvA{=1 v  gggfg sssfsdfwgergre'
name_val = re.sub(r'\D+$', '', name_val).replace(" ", '')
print(name_val)
