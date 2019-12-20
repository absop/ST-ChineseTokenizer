import re
import sublime
import sublime_plugin

from . import jieba


"""没有生命，地球的脸面就会失去，变得像月球般木然。
"""
regex = r'[\u4E00-\u9FA5\s]+'
chinese_regex = re.compile(r'[^\x00-\x7F]+')
find_results_match = re.compile(r'\d+:')

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


class ChineseTokenizerAddSelection(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.sel().add(self.region)


class ChineseTokenizerListener(sublime_plugin.EventListener):
    def on_text_command(self, view, name, args):
        if name == "drag_select" and args.get("by", "") == "words":
            event = args["event"]
            point = view.window_to_text((event["x"], event["y"]))
            # constant.numeric.line-number.match.find-in-files
            # entity.name.filename.find-in-files
            # 避免 Find Results 里面点击打开文件的功能失效，暂时不做长行优化
            if ("filename.find-in-files" in view.scope_name(point) or
                find_results_match.search(view.substr(view.line(point)))):
                return None

            neaset_region = view.sel()[0]
            regions = []
            for r in view.sel():
                regions.append(r)
                if r.empty() and neaset_region.a < r.a and r.a <= point:
                    neaset_region = r

            if neaset_region.empty():
                point = neaset_region.a

            region = expand_word(view, point, True)

            ChineseTokenizerAddSelection.region = region
            return "chinese_tokenizer_add_selection"


def plugin_loaded():
    sublime.set_timeout_async(jieba.initialize, 0)
