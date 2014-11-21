#!/usr/bin/env python
# encoding: utf-8

from bs4 import BeautifulSoup, Comment
import urllib
import re


# html 标签白名单
VALID_TAGS = {
    'strong': [],
    'em': [],
    'span': {'style', },
    'p': [],
    'h1': [],
    'pre': [],
    'h2': [],
    'h3': [],
    'br': [],
    'a': {'href', 'title'},
    'img': {'src', 'style'},  # 外链图片缓存
    'embed': {'type', 'class', 'src', 'width', 'height', 'allowfullscreen', 'allowscriptaccess',
              'loop', 'menu', 'play', 'src', 'style', 'wmode'}  # 特别处理
}


def get_url_host(url):
    """ url中获取域名
    """
    pro, rest = urllib.splittype(url)
    if not rest:
        return None
    host, rest = urllib.splithost(rest)
    return host


def __valid_attr(tag, attrs):
    re_attrs = dict()
    if tag == 'span':
        valid = {'background-color', 'line-height', 'color', 'font-size'}
        attr = attrs.get('style')
        if attr:
            values = re.findall(r'([\w-]+):', attr)
            if set(values).issubset(valid):
                re_attrs['style'] = attr
    elif tag == 'embed':
        #
        # b站: http://share.acg.tv/flash.swf?aid=406209&page=1
        # a站: http://static.acfun.mm111.net/player/ACFlashPlayer.out.swf?type=page&url=http://www.acfun.tv/v/ac1509412
        # c站: http://www.tucao.cc/mini/4040389.swf
        # 土豆:
        #
        default_attr_settings = {
            'allowfullscreen': 'true',
            'allowscriptaccess': 'never',
            'class': ['edui-faked-video'],
            'loop': 'false',
            'menu': 'false',
            'play': 'true',
            'style': 'float:none',
            'pluginspage': 'http://www.macromedia.com/go/getflashplayer',
            'type': 'application/x-shockwave-flash',
            'wmode': 'transparent'
        }
        # todo 支持 奇异, 搜狐, 优酷, 土豆, 乐视等
        allow_src_host = {'share.acg.tv', 'static.acfun.mm111.net', 'www.tucao.cc'}
        # 检测播放源地址, 只允许固定网站的源
        src_value = attrs.get('src')
        if src_value:
            host = get_url_host(src_value)
            if host in allow_src_host:  # todo 添加提示
                re_attrs['src'] = src_value
        re_attrs.update(default_attr_settings)
    else:
        valid_attrs = VALID_TAGS.get(tag)
        for at in valid_attrs:
            v = attrs.get(at)
            if v:
                re_attrs[at] = v
    if tag == 'a':
        re_attrs['target'] = '_blank'
    return re_attrs


def sanitize_html(value, valid_tags=VALID_TAGS):
    """ HTML 富文本过滤
    参考: https://stackoverflow.com/questions/699468/python-html-sanitizer-scrubber-filter
    """
    soup = BeautifulSoup(value)
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]
    out = soup.renderContents()
    while 1:
        out = out
        soup = BeautifulSoup(out)
        for tag in soup.findAll(True):
            if tag.name not in valid_tags:
                tag.hidden = True
            else:
                # attrs is a dict
                tag.attrs = __valid_attr(tag.name, tag.attrs)
        out = soup.renderContents()
        if out == out:
            break
    return out
