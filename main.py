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

    if region.begin() >= point:
        region = region.cover(view.word(point - 1))
    if region.end() <= point:
        region = region.cover(view.word(point + 1))

    content = view.substr(region)
    if chinese_regex.search(content):
        words = jieba.cut(content)
        start_point = region.begin()
        for word in words:
            end_point = start_point + len(word)
            region = sublime.Region(start_point, end_point)
            if (region.begin() <= point and region.end() > point or
                region.begin() >= point and forward or
                region.end() >= point and not forward):
                break
            start_point = end_point

    return region


class ChineseTokenizerDeleteWord(sublime_plugin.TextCommand):
    def run(self, edit, forward=False):
        regions, view = [], self.view
        if forward:
            for r in view.sel():
                region = expand_word(view, r.begin(), True)
                if r.empty() and region.a < r.a:
                    region.a = r.a;
                regions.append(region)
        else:
            for r in view.sel():
                region = expand_word(view, r.end(), False)
                if r.empty() and region.b > r.b:
                    region.b = r.b;
                regions.append(region)

        for r in reversed(regions):
            view.erase(edit, r)


class ChineseTokenizerMove(sublime_plugin.TextCommand):
    def run(self, edit, forward=True, extend=False):
        regions, view = [], self.view
        if forward:
            for r in view.sel():
                region = expand_word(view, r.end(), True)
                if extend or r.empty() and region.a < r.a:
                    region.a = r.a;
                else:
                    region = region.end()
                regions.append(region)
        else:
            for r in view.sel():
                region = expand_word(view, r.begin(), False)
                if extend or r.empty() and region.b > r.b:
                    region.b = r.b;
                else:
                    region = region.begin()
                regions.append(region)

        view.sel().clear()
        view.sel().add_all(regions)


class ChineseTokenizerListener(sublime_plugin.EventListener):
    def expand_selection(self, view, point):
        region = expand_word(view, point, True)
        regions = [r for r in view.sel()]
        view.sel().clear()
        region.b -= 1
        view.sel().add(region)
        view.run_command("move",
            {"by": "characters", "extend": True, "forward": True})
        view.sel().add_all(regions)

    def on_text_command(self, view, name, args):
        if name == "drag_select" and args.get("by", "") == "words":
            event = args["event"]
            point = view.window_to_text((event["x"], event["y"]))
            self.expand_selection(view, point)
            return (name, args)

