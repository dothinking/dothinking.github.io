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
    

    def to_meta_page(self, category_dir_name:str):
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
        meta = f'发布于：{self.year}-{self.month}-{self.day}'
        if self.categories:
            links = [f'[{c}]({category_dir_name}/{to_dir_name(c)}.md)' for c in self.categories]
            meta += ' | 分类：' + ' , '.join(links)
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

    INDEX_FILENAME   = 'index.md'
    ARCHIVE_FILENAME = 'archive.md'
    ABOUT_FILENAME   = 'about.md'

    def __init__(self, docs_dir:str, category_dir_name:str='categories', archive_dir_name:str='archives') -> None: 
        self.docs_dir = docs_dir
        self.category_dir_name = category_dir_name
        self.archive_dir_name = archive_dir_name

        self._posts = defaultdict(list) # summarized by year/category
        self._archives = set()
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
        self._archives.add(post.year)

        # by category
        for c in (post.categories or ['未分类']):
            self._posts[c].append(post)
            self._categories.add(c)


    def to_category_pages(self):
        '''Create summary pages grouped by category.'''
        page_dir = os.path.join(self.docs_dir, self.category_dir_name)
        for c in self._categories:
            self._to_summary_page(c, page_dir)
 

    def to_archive_pages(self):
        '''Create summary pages grouped by year.'''
        lines = ['## Archives\n']
        page_dir = os.path.join(self.docs_dir, self.archive_dir_name)
        for year in sorted(self._archives, reverse=True):
            len_posts = len(self._posts.get(year))
            lines.append(f'- [{year} ({len_posts})]({self.archive_dir_name}/{year}.md)')

            # pages in each year
            self._to_summary_page(year, page_dir)
        
        # top page
        with open(os.path.join(self.docs_dir, Posts.ARCHIVE_FILENAME), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))            


    def to_home_page(self, title:str='', count:int=5):
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
            len_posts = len(self._posts.get(c))
            lines.append(f'- [{c} ({len_posts})]({self.category_dir_name}/{to_dir_name(c)}.md)')

        with open(os.path.join(self.docs_dir, Posts.INDEX_FILENAME), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


    def to_navigation(self) -> str:
        '''Generate grouped navigation.

        ::
            nav:                
                - '分类':
                    - 'foo': categories/foo.md
                    - 'bar': categories/bar.md
                - '归档': archives.md
                - '关于': about.md
                ...
        '''
        nav = ['nav:']
        nav.append("  - '分类':")
        for c in sorted(self._categories):
            nav.append(f'    - {c}: {self.category_dir_name}/{to_dir_name(c)}.md')
        
        # archive, about
        nav.extend([
            f'  - 归档: {Posts.ARCHIVE_FILENAME}',
            f'  - 关于: {Posts.ABOUT_FILENAME}'
        ])
        
        return '\n'.join(nav)

 
    def to_meta_pages(self):
        '''Update page content with meta-date included.'''
        for year in self._archives:
            for post in self._posts.get(year, []):
                post.to_meta_page(self.category_dir_name)


    def _get_latest(self, count:int):
        posts = []
        need = count
        for year in sorted(self._archives, reverse=True):
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
            f.write(self.content + '\n' + more_content)



def run(cfg_file_path:str,
        archive_path_name:str='archives', 
        category_path_name:str='categories', 
        latest_posts_count:int=5,
        update_page:bool=False):
    
    # collect all posts
    build_dir = os.path.dirname(cfg_file_path)
    docs_dir = os.path.join(build_dir, 'docs')
    posts = Posts(docs_dir, category_path_name, archive_path_name)
    
    # summary pages by category and year
    posts.to_category_pages()
    posts.to_archive_pages()

    # update config file
    cfg = ConfigFile(cfg_file_path)
    cfg.update(posts.to_navigation())
    
    # create index page only if not exist
    if not os.path.exists(os.path.join(docs_dir, Posts.INDEX_FILENAME)):
        title = cfg.get_site_info()
        posts.to_home_page(title, latest_posts_count)
    
    # include meta-data to page
    if update_page: 
        posts.to_meta_pages()
    
    


if __name__=='__main__':
    import sys

    command, cfg_file, archive_name, categories_name, latest_count = sys.argv[1:]
    latest_count = int(latest_count)
    run(cfg_file, archive_name, categories_name, latest_count, command=='build')