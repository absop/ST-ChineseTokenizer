# Chinese Words Cutter (中文分词)

Sublime Text 3 的 jieba 分词库绑定，支持对中文更精确地选词、删词和按词移动光标。

[插件效果](#operation-demo操作演示)见本文末尾。

# Install（安装）

给[Sublime Text](http://sublimetext.com)安装插件，最简单的方法是使用[Package Control](packagecontrol.io)（需要网络），前提是该插件已经被Package Control接受。

下面是安装步骤

1. 按快捷键<kbd>ctrl+shift+p</kbd>打开命令面板
2. 输入 pcip (Package Control: Install Package)，然后<kbd>Enter</kbd>，等待Package Control加载插件信息
3. 输入 cwc (Chinese Word Cutter), 然后<kbd>Enter</kbd>，等待安装完毕

# Usage（使用方法）

1. 修改 **Sublime Text** 的`word_separators`设置为
```
"./\\()\"'-:,.;<>~!@#$%^&*|+=[]{}`~?（《【，。—·…！￥：；‘“”’？、】》）"
```

2. 了解一下功能和对应的快捷键

   | 快捷键                     | 功能             |
   | -------------------------- | ---------------- |
   | <kbd>alt+backspace</kbd>   | 向后删除一个单词 |
   | <kbd>alt+delete</kbd>      | 向前删除一个单词 |
   | <kbd>alt+left</kbd>        | 后退一个单词     |
   | <kbd>alt+right</kbd>       | 前进一个单词     |
   | <kbd>alt+shift+left</kbd>  | 向后选中一个单词 |
   | <kbd>alt+shift+right</kbd> | 向前选中一个单词 |

   Sublime 自己就提供了这些功能，但对中文支持不好，本插件只是在它的基础上添加对中文的支持，用法基本上与默认的一致。

3. 鼠标双击选中单词

   默认情况下，在Sublime里面双击中文，整个段都会被选中。因为Sublime是按照它的`word_separators`设置和语法文件来分割文本产生单词序列的，而中文词语之间没有分隔符，所以Sublime识别不了中文词语。本插件解决了这一问题。

4. <kbd>ctrl+d</kbd>增量选中当前单词的功能尚未对中文实现。

# Operation demo（操作演示）
![](images/cwc.gif)

