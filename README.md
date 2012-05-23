SlideGen 是一个使用YML和markdown生成html5幻灯的工具，预制了多种版式，预计支持多种幻灯引擎(desk.js,S5,Impress.js)，提供一次编码，可生成多种引擎，多种主题的幻灯。避免你学习多个幻灯引擎的时间精力消耗。


文档地址: [这里](http://packages.python.org/SlideGen/)
安装方法:
* git clone 这个版本库，然后python setup.py install
* 或者。 easy_install SlideGen

## 目前状态
* 版本 pre-V0.0.0.1
* 支持的引擎
	* desk.js
* 支持的版式
	* topic
	* layout
	* one
	* two
	* takahashi
	* takahashi-group
	* list_group

## RoadMap
### @todo
* 将该库port到SAE，可以云端编辑

### V0.0.0.1
* 完成基本的功能
* 添加setuptools支持
* 尝试自己用SlideGen生成SlideGen的介绍幻灯
* 使用SlideGen做一个自己的Presentation