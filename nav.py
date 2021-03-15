# -*-coding:utf-8 -*-

import os
import datetime
from collections import defaultdict


def nav(path, count=5):
    # filename: yyyy-mm-dd-xxxx.md
    s = len('yyyy-mm-dd') + 1
    e = -len('.md')

    # current year
    latest = datetime.datetime.now().year

    # sort by date
    filenames = [name for name in os.listdir(path)]
    filenames.sort(reverse=True)

    posts = defaultdict(list)
    for name in filenames:
        year = name[0:4]
        if not all([i.isdigit() for i in year]): continue
        item = f"    - '{name[s:e]}': {name}"
        if latest-int(year)>=count:
            posts['More'].append(item)
        else:
            posts[year].append(item)

    # final string
    res = ['\nnav:']
    for k,v in posts.items():
        res.append(f'  - {k}:')
        res.append('\n'.join(v))
    
    return '\n'.join(res)



if __name__=='__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(nav(sys.argv[1]))