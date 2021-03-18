# -*-coding:utf-8 -*-

import os
import re
from collections import defaultdict


class Post:
    # yyyy-mm-dd-post_title.md
    NAME_PATTERN = re.compile(r'(?P<YEAR>\d{4})-(?P<MONTH>\d{2})-(?P<DAY>\d{2})-(?P<TITLE>.*).md')

    def __init__(self, filename:str) -> None:
        self.filename = filename
        res = Post.NAME_PATTERN.match(filename)
        matched = res is not None
        self.year = res.group('YEAR') if matched else None
        self.month = res.group('MONTH') if matched else None
        self.day = res.group('DAY') if matched else None
        self.title = res.group('TITLE') if matched else None
   
    def to_line(self, path:str):
        return f'- `{self.year}-{self.month}-{self.day}` [{self.title}]({path}/{self.filename})'


class Posts:

    def __init__(self, posts:list=None) -> None:
        self._posts = defaultdict(list)
        self.extend(posts or [])

    def append(self, post:Post):
        if not isinstance(post, Post) or post.year is None: return
        self._posts[post.year].append(post)
    
    def extend(self, posts:list):
        for post in posts: self.append(post)

    def _sub_page(self, year:str, path:str):
        lines = [f'## {year}\n\n']
        for post in self._posts.get(year, []):
            lines.append(post.to_line(path))
        return '\n'.join(lines)
    
    def to_nav(self, sub_path:str, count:int=5):
        '''Generate grouped navigation.

        ::
            nav:
                - '2021': sub_path/2021.md
                - '2020': sub_path/2020.md
                ...
                - 'More':
                    - '2015': sub_path/2015.md
                    - '2014': sub_path/2014.md

        Args:
            sub_path (str): Full path Storing annual posts.
            count (int, optional): The count of year shown in navigation. Defaults to 5.
        '''
        group_posts = {}
        group_posts['More'] = defaultdict(dict)

        top = ['\n', 'nav:']
        more = ['\n', "  - 'More':"]
        path_name = os.path.basename(sub_path)
        i = 0
        for year in self._posts:            
            i += 1
            # create annual posts summary page
            with open(os.path.join(sub_path, f'{year}.md'), 'w', encoding='utf-8') as f:
                f.write(self._sub_page(year, '..'))

            # navigation
            item = f'- {year}: {path_name}/{year}.md'
            if i <= count:
                top.append(f'  {item}')
            else:
                more.append(f'    {item}')
        
        # about
        about = '\n  - 关于: about.md'
        
        return '\n'.join(top) + '\n'.join(more) + about



def nav(path, sub_path_name:str='_categories', count=5):
    # sort by date
    filenames = [filename for filename in os.listdir(path)]
    filenames.sort(reverse=True)

    items = [Post(filename) for filename in filenames]
    posts = Posts(items)    
    return posts.to_nav(os.path.join(path, sub_path_name), count)



if __name__=='__main__':
    import sys
    # sys.stdout.reconfigure(encoding='utf-8') # python>=3.7
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
    text = nav(sys.argv[1], sys.argv[2])
    print(text)