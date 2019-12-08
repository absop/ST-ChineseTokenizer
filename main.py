# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import re

from . import jieba

jieba.initialize()

"""没有生命，地球的脸面就会失去，变得像月球般木然。
"""
regex = r'[\u4E00-\u9FA5\s]+'
chinese_regex = re.compile(r'[^\x00-\x7F]+')


def expand_word(view, point: int, forward: bool) -> sublime.Region:
    region = view.word(point)

    if not forward and region.begin() >= point:
        # region = region.cover(view.word(point - 1))
        region = sublime.Region(view.word(point - 1).begin(), point)
    if forward and region.end() <= point:
        # region = region.cover(view.word(point + 1))
        region = sublime.Region(point, view.word(point + 1).end())

    content = view.substr(region)
    if chinese_regex.search(content):
        words = jieba.cut(content)
        start_point = region.begin()
        if forward:
            for word in words:
                end_point = start_point + len(word)
                if start_point >= point or end_point > point:
                    region = sublime.Region(start_point, end_point)
                    break
                start_point = end_point
        else:
            for word in words:
                end_point = start_point + len(word)
                if end_point >= point:
                    region = sublime.Region(end_point, start_point)
                    break
                start_point = end_point
    else:
        if not forward:
            region.a, region.b = region.b, region.a

    # print("%s[%s][%s]" % (region, forward, view.substr(region)))
    return region


class ChineseTokenizerDeleteWord(sublime_plugin.TextCommand):
    def run(self, edit, forward=False):
        regions, view = [], self.view
        if forward:
            for r in view.sel():
                region = expand_word(view, r.begin(), True)
                if r.empty() and region.a < r.a:
                    region.a = r.a
                regions.append(region)
        else:
            for r in view.sel():
                region = expand_word(view, r.end(), False)
                if r.empty() and region.a > r.a:
                    region.a = r.a
                regions.append(region)

        for r in reversed(regions):
            view.erase(edit, r)


class ChineseTokenizerMove(sublime_plugin.TextCommand):
    def run(self, edit, forward=True, extend=False):
        regions, view = [], self.view
        if forward:
            for r in view.sel():
                region = expand_word(view, r.b, True)
                if not extend:
                    region = region.end()
                else:
                    region.a = r.a
                    if region.b <= r.b:
                        region.b = r.b + 1
                regions.append(region)
        else:
            for r in view.sel():
                region = expand_word(view, r.b, False)
                if not extend:
                    region = region.begin()
                else:
                    region.a = r.a
                    if region.b >= r.b:
                        region.b = r.b - 1
                regions.append(region)

        view.sel().clear()
        view.sel().add_all(regions)


class ChineseTokenizerAddRegion(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.sel().add(self.region)


class ChineseTokenizerListener(sublime_plugin.EventListener):
    def on_text_command(self, view, name, args):
        if name == "drag_select" and args.get("by", "") == "words":
            event = args["event"]
            point = view.window_to_text((event["x"], event["y"]))
            # TODO: Make it run asynchronously
            ChineseTokenizerAddRegion.region = expand_word(view, point, True)

            return "chinese_tokenizer_add_region"
