# -*-coding:utf-8 -*-

import os
import re
from collections import defaultdict


def to_dir_name(name:str):
    return name.replace('/', '-')


class Post:
    # yyyy-mm-dd-post_title.md
    NAME_PATTERN = re.compile(r'(?P<YEAR>\d{4})-(?P<MONTH>\d{2})-(?P<DAY>\d{2})-(?P<TITLE>.*).md')
    
    HLINE = '---'

    def __init__(self, post_path:str) -> None:
        ''' post structure:        
                ---
                categories: [foo, bar, ...]
                tags: [this, that, ...]
                ---
                
                # title
                
                ---
                
                content
        '''
        # get year-month-day-title from filename
        self.post_path = post_path
        self._process_filename()

        # get meta-data from content
        with open(post_path, 'r', encoding='utf-8') as f:
            src = f.read().strip()
        if not src:
            self.meta, self.content = None, None
        else:
            self._process_content(src)
        
        # check categories
        self.categories = self._process_categories() if self.meta else None
    

    def to_meta_page(self, dir_name:str):
        lines = []

        # meta area
        if self.meta:
            lines.append(Post.HLINE)
            lines.extend(self.meta)
            lines.append(Post.HLINE)
        
        # title area: always has a title
        lines.append('\n')
        lines.append(f'# {self.title}')
        lines.append('\n')
        meta = f'{self.year}-{self.month}-{self.day}'
        if self.categories:
            links = [f'[{c}]({dir_name}/{to_dir_name(c)}.md)' for c in self.categories]
            meta += ' | ' + ' , '.join(links)
        lines.append(meta)
        lines.append('\n')
        lines.append(Post.HLINE)

        # content
        if self.content:
            lines.append('\n')
            lines.extend(self.content)
        
        with open(self.post_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


    def to_hyperlink(self, rel_path:str='.'):
        filename = os.path.basename(self.post_path)
        return f'- `{self.year}-{self.month}-{self.day}` [{self.title}]({rel_path}/{filename})'


    def _process_filename(self):
        filename = os.path.basename(self.post_path)
        res = Post.NAME_PATTERN.match(filename)
        matched = res is not None
        self.year = res.group('YEAR') if matched else None
        self.month = res.group('MONTH') if matched else None
        self.day = res.group('DAY') if matched else None
        self.title = res.group('TITLE').replace('-', ' ') if matched else None
    

    def _process_content(self, src:str):
        lines = src.splitlines()
        # potential meta
        self.meta = []
        next_i = 0
        if lines[0].startswith(Post.HLINE): 
            for i, line in enumerate(lines[1:], start=1) :
                s = line.strip()
                if s == '': continue
                if ':' in s: 
                    self.meta.append(s)
                elif s.startswith(Post.HLINE): # normal end of meta
                    next_i = i+1
                    break
                else: # not valid meta
                    self.meta = None
                    break        
        self._extract_title_and_content(lines[next_i:])


    def _process_categories(self):
        for line in self.meta:
            if not line.strip().startswith('categories'): continue
            text = line[len('categories')+1:].strip('[ ]')
            return [c.strip() for c in text.split(',')]


    def _extract_title_and_content(self, lines):
        '''extract title starting with `# ` and content right after `---`.'''
        next_i = 0
        for i, line in enumerate(lines):
            s = line.strip()
            if s == '': 
                continue
            elif s.startswith('# '):
                self.title = line[2:].strip() # overwrite title extracted from filename
                next_i = i+1
                break
            else:
                break        

        self._extract_content(lines[next_i:])


    def _extract_content(self, lines):
        '''check start of content: right after `---`'''
        start = None
        for i, line in enumerate(lines):
            s = line.strip()
            if s == '': 
                continue
            else:
                start = i+1 if s.startswith(Post.HLINE) else i
                break
        self.content = lines[start:] if start else None



class Posts:

    def __init__(self, docs_dir:str) -> None: 
        self.docs_dir = docs_dir
        self._posts = defaultdict(list) # summarized by year/category
        self._years = set()
        self._categories = set()
        
        for filename in sorted(os.listdir(docs_dir), reverse=True):            
            post_path = os.path.join(docs_dir, filename)
            if not os.path.isfile(post_path): continue
            post = Post(post_path)
            self.append(post)


    def append(self, post:Post):
        if not isinstance(post, Post) or post.year is None: return
        # by year
        self._posts[post.year].append(post)
        self._years.add(post.year)

        # by category
        for c in (post.categories or ['未分类']):
            self._posts[c].append(post)
            self._categories.add(c)


    def summay_categories(self, dir_name:str):
        '''Create summary pages grouped by category.'''
        page_dir = os.path.join(self.docs_dir, dir_name)
        for c in self._categories:
            self._to_summary_page(c, page_dir)
 

    def summay_years(self, dir_name:str):
        '''Create summary pages grouped by year.'''
        page_dir = os.path.join(self.docs_dir, dir_name)
        for year in self._years:
            self._to_summary_page(year, page_dir)


    def to_index(self, dir_name:str, title:str='', count:int=5):
        '''Create home page with latest posts and categories.'''
        lines = [title]

        # latest posts
        lines.append('## 最近更新\n')
        for post in self._get_latest(count):
            lines.append(post.to_hyperlink('.'))

        # categories
        lines.append('\n')
        lines.append('## 更多分类\n')
        for c in sorted(self._categories):
            lines.append(f'- [{c} ({len(self._posts.get(c))})]({dir_name}/{to_dir_name(c)}.md)')

        with open(os.path.join(self.docs_dir, 'index.md'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


    def to_navigation(self, dir_name:str, count:int=5) -> str:
        '''Generate grouped navigation.

        ::
            nav:
                - '2021': dir_name/2021.md
                - '2020': dir_name/2020.md
                ...
                - 'More':
                    - '2015': dir_name/2015.md
                    - '2014': dir_name/2014.md

        Args:
            dir_name (str): Dir name storing annual posts.
            count (int, optional): The count of year shown in navigation. Defaults to 5.
        '''
        group_posts = {}
        group_posts['More'] = defaultdict(dict)

        top = ['\n', 'nav:']
        more = ['\n', "  - 'More':"]
        i = 0

        for year in sorted(self._years, reverse=True):            
            i += 1
            # navigation
            item = f'- {year}: {dir_name}/{year}.md'
            if i <= count:
                top.append(f'  {item}')
            else:
                more.append(f'    {item}')
        
        # about
        about = '\n  - 关于: about.md'
        
        return '\n'.join(top) + '\n'.join(more) + about

 
    def to_meta_pages(self, dir_name:str):
        '''Update page content with meta-date included.'''
        for year in self._years:
            for post in self._posts.get(year, []):
                post.to_meta_page(dir_name)


    def _get_latest(self, count:int):
        posts = []
        need = count
        for year in sorted(self._years, reverse=True):
            year_posts = self._posts.get(year)
            year_cnt = len(year_posts)
            if year_cnt>=need:
                posts.extend(year_posts[0:need])
                break
            else:
                posts.extend(year_posts)
                need -= year_cnt
        return posts


    def _to_summary_page(self, category:str, page_dir:str):
        '''Store summary page under page_dir/category.md.'''
        lines = [f'## {category}\n\n']
        for post in self._posts.get(category, []):
            lines.append(post.to_hyperlink('..'))
        text = '\n'.join(lines)

        with open(os.path.join(page_dir, f'{to_dir_name(category)}.md'), 'w', encoding='utf-8') as f:
            f.write(text)



class ConfigFile:
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        # read content
        with open(file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def get_site_info(self):
        pattern = re.compile(r'site_name:(?P<site>.*)\n(.*)site_description:(?P<desp>.*)\n')
        match = pattern.search(self.content)
        if match:
            site = match.group('site').strip()
            description = match.group('desp').strip()
        else:
            site = 'My Blog'
            description = 'Welcome to my blog'
        return f'# {site}\n\n{description}\n\n---\n\n'


    def update(self, more_content):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(self.content + more_content)



def run(cfg_file_path:str,
        year_path_name:str='years', 
        category_path_name:str='categories', 
        nav_count:int=5,
        latest_count:int=5,
        update_page:bool=False):
    
    # collect all posts
    build_dir = os.path.dirname(cfg_file_path)
    docs_dir = os.path.join(build_dir, 'docs')
    posts = Posts(docs_dir)
    
    # summary pages by category and year
    posts.summay_categories(category_path_name)
    posts.summay_years(year_path_name)

    # update config file
    cfg = ConfigFile(cfg_file_path)
    cfg.update(posts.to_navigation(year_path_name, nav_count))
    
    # create index page only if not exist
    if not os.path.exists(os.path.join(docs_dir, 'index.md')):
        title = cfg.get_site_info()
        posts.to_index(category_path_name, title, latest_count)
    
    # include meta-data to page
    if update_page: 
        posts.to_meta_pages(category_path_name)
    
    


if __name__=='__main__':
    import sys

    command, cfg_file, years_name, categories_name, nav_count, latest_count = sys.argv[1:]
    nav_count = int(nav_count)
    latest_count = int(latest_count)
    run(cfg_file, years_name, categories_name, nav_count, latest_count, command=='build')