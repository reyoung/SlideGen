#*-* coding=utf-8
import re
import functools
import yaml
import tornado.template
DEBUG=True
DEFAULT_CONFIG={
    "GRAMMA_VERSION":1,
    "ENGINE":"Desk.js",
    "THEME":"web-2.0",
    "ENGINE_PATH":"Deskjs/",
    "AUTHOR":{
        "name":"Nobody",
        "email":"Nobody@nocompany.com"
    },
    "TITLE":"Default Title"
}


DESKJS_TEMPLATE=r'''{% autoescape None %}
<!DOCTYPE html>
<html class="js flexbox canvas canvastext webgl no-touch geolocation postmessage websqldatabase indexeddb hashchange history draganddrop websockets rgba hsla multiplebgs backgroundsize borderimage borderradius boxshadow textshadow opacity cssanimations csscolumns cssgradients cssreflections csstransforms csstransforms3d csstransitions fontface generatedcontent video audio localstorage sessionstorage webworkers applicationcache svg inlinesvg smil svgclippaths ready" lang="en"><!--<![endif]--><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    
    <title>{{title}}</title>
    <style type="text/css">
{{custom_css}}
    </style>
    <meta name="author" content="{{author_name}} {{author_email}}">
    <meta name="viewport" content="width=1024, user-scalable=no">
    
    <!-- Core and extension CSS files -->
    <link rel="stylesheet" href="{{path}}/core/deck.core.css">
    <link rel="stylesheet" href="{{path}}/extensions/goto/deck.goto.css">
    <link rel="stylesheet" href="{{path}}/extensions/menu/deck.menu.css">
    <link rel="stylesheet" href="{{path}}/extensions/navigation/deck.navigation.css">
    <link rel="stylesheet" href="{{path}}/extensions/status/deck.status.css">
    <link rel="stylesheet" href="{{path}}/extensions/hash/deck.hash.css">
    <link rel="stylesheet" href="{{path}}/extensions/scale/deck.scale.css">
    <!-- Style theme. More available in /themes/style/ or create your own. -->
    <link rel="stylesheet" href="{{path}}/themes/style/{{theme}}.css">
    
    <!-- Transition theme. More available in /themes/transition/ or create your own. -->
    <link rel="stylesheet" href="{{path}}/themes/transition/horizontal-slide.css">
    
    <script src="{{path}}/modernizr.custom.js"></script>
</head>
<body class="deck-container on-slide-0 on-slide-title-slide">

<!-- Begin slides -->

<!-- deck.navigation snippet -->
<a href="#" class="deck-prev-link" title="Previous">&#8592;</a>
<a href="#" class="deck-next-link" title="Next">&#8594;</a>

<!-- deck.status snippet -->
<p class="deck-status">
    <span class="deck-status-current"></span>
    <span class="deck-status-total"></span>
</p>

<!-- deck.goto snippet -->
<form action="." method="get" class="goto-form">
    <label for="goto-slide">Go to slide:</label>
    <input type="text" name="slidenum" id="goto-slide" list="goto-datalist">
    <datalist id="goto-datalist"></datalist>
    <input type="submit" value="Go">
</form>

<!-- deck.hash snippet -->
<a href="." title="Permalink to this slide" class="deck-permalink">#</a>

{{slide_content}}

<!-- Grab CDN jQuery, with a protocol relative URL; fall back to local if offline -->
<script src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.7.min.js"></script>
<script>window.jQuery || document.write('<script src="{{path}}/jquery-1.7.min.js"><\/script>')</script>

<!-- Deck Core and extensions -->
<script src="{{path}}/core/deck.core.js"></script>
<script src="{{path}}/extensions/hash/deck.hash.js"></script>
<script src="{{path}}/extensions/menu/deck.menu.js"></script>
<script src="{{path}}/extensions/goto/deck.goto.js"></script>
<script src="{{path}}/extensions/status/deck.status.js"></script>
<script src="{{path}}/extensions/navigation/deck.navigation.js"></script>
<script src="{{path}}/extensions/scale/deck.scale.js"></script>
<!-- Initialize the deck -->
<script>
$(function() {
    $.deck('.slide');
    $.deck('enableScale');
});
</script>
</body>
</html>'''



def LexAnalysis(method):
    @functools.wraps(method)
    def wrapper(*args, **kwds):
        content = args[1]
        yml = yaml.safe_load(content)
        return method(*args,yml=yml,**kwds)
    return wrapper

def WrapID(method):
    @functools.wraps(method)
    def wrapper(*args, **kwds):
        data = kwds['yml'].values()[0]
        if 'id' not in data:
            data['id']=None
        kwds['yml'].values()[0] = data
        return method(*args,**kwds)
    return wrapper


class SlideGener(object):
    def __init__(self,content):
        self.__content = content
        self.__settings=DEFAULT_CONFIG
        self.__setting_handler={
                "config":self.__handle_config_settings,
                "layout":self.__handle_layout_settings,
                "css":self.__handle_css_settings
        }
        self.__slide_handler={
                "topic": {"Desk.js":self.__handle_topic_slide_with_deskjs},
                "layout":{"Desk.js":self.__handle_layout_slide_with_deskjs},
                "takahashi":{"Desk.js":self.__handle_takahashi_slide_with_deskjs},
                "one":{"Desk.js":self.__handle_one_slide_with_deskjs}
        }
        self.__gener_handler={
                "Desk.js":self.__gen_content_deskjs
        }
        
        self.__custom_css=""
        
    def process(self):
        matcher = re.compile("^[A-Za-z$].*:",re.MULTILINE)
        it = matcher.finditer(self.__content)
        pre_result = None
        try:
            while True:
                result = it.next()
                if pre_result != None:
                    begin=pre_result.start()
                    end=result.start()
                    self.handleBlock(begin, end)
                pre_result = result
        except:
            begin=pre_result.start()
            end=len(self.__content)
            self.handleBlock(begin, end)
        
    def gen_content(self):
        return self.__gener_handler[self.__settings['ENGINE']]()
    
    def __gen_content_deskjs(self):
        template = tornado.template.Template(DESKJS_TEMPLATE)
        result = template.generate(slide_content=self.__deskjs_contents,
                                   title = self.__settings['TITLE'],
                                   author_name=self.__settings['AUTHOR']['name'],
                                   author_email=self.__settings['AUTHOR']['email'],
                                   path=self.__settings['ENGINE_PATH'],
                                   theme=self.__settings['THEME'],
                                   custom_css = self.__custom_css
                                   )
        return result
    
    def handleSlideBlock(self, content):
        matcher = re.compile("^(.*):",re.MULTILINE)
        result = matcher.match(content)
        command=result.group(1)
        engine = self.__settings["ENGINE"]
        self.__slide_handler[command][engine](content)
    
    def handleSettingBlock(self, content):
        matcher = re.compile("^\$(.*):",re.MULTILINE)
        result = matcher.match(content)
        command=result.group(1)
        self.__setting_handler[command](content)
    
    def handleBlock(self,begin,end):
        if self.__content[begin]=="$":
            self.handleSettingBlock(self.__content[begin:end])
        else:
            self.handleSlideBlock(self.__content[begin:end])
            
    @LexAnalysis
    def __handle_config_settings(self,content,yml=None):
        for k in yml['$config']:
            upper_k = k.upper()
            if upper_k in self.__settings:
                self.__settings[upper_k] = yml['$config'][k]
    @LexAnalysis
    def __handle_layout_settings(self,content,yml=None):
        self.__layout_settings = yml['$layout']
    
    @LexAnalysis
    def __handle_css_settings(self,content,yml=None):
        self.__custom_css = yml["$css"]

    @LexAnalysis
    def __handle_topic_slide_with_deskjs(self,content,yml=None):
        id = "topic"
        content = yml['topic']
        template_str = r'''
<div class="slide" id="{{id}}">
<h1>{{content}}</h1>
</div>'''
        template = tornado.template.Template(template_str)
        result = template.generate(id=id,content=content)
        self.__addDeskjsSlide(result)
        
    @LexAnalysis
    def __handle_layout_slide_with_deskjs(self,content,yml=None):
        try:
            data_0 = self.__layout_settings
            data_1 = yml['layout']
            for k in data_1:
                data_0[k]=data_1[k]
            if 'select' not in data_0:
                data_0['select']='all'
            template_str=r'''
<div class="slide" id="layout_{{select}}">
<h2>{{title}}</h2>
<ul class="layout_item">{% set count = 0 %}
    {% for c in content %}
        {% if select == 'all' or count == int(select) %}
        <li ><h3 class="layout_selected">{{c}}</h3></li>
        {% else %}
        <li ><h3 class="layout_unselected">{{c}}</h3></li>
        {% end %}{% set count += 1 %}
    {% end %}
</ul>
</div>'''
            template=tornado.template.Template(template_str)
            self.__addDeskjsSlide(template.generate(**data_0))
        except:
            raise RuntimeError("You Need $layout Before")
    
    
    @LexAnalysis
    @WrapID
    def __handle_takahashi_slide_with_deskjs(self,content,yml=None):
        template_str=r'''
<div class="slide takahashi" {% if id!=None %}id="{{id}}"{% end %}>
<h1>{{title}}</h1>
<h3>{{desc}}</h3>
</div>'''
        data = yml['takahashi']
        self.__addDeskjsSlide(tornado.template.Template(template_str).generate(**data))

    @LexAnalysis
    @WrapID
    def __handle_one_slide_with_deskjs(self,content,yml=None):
        template_str=r'''<div class="slide one" {% if id!=None %}id="{{id}}"{% end %}>
<h2>{{title}}</h2>
{% autoescape None %}
{{processed_content}}
</div>'''
        data = yml['one']
        self.__addDeskjsSlide(tornado.template.Template(template_str).generate(processed_content=self.__render_deskjs_content(data['content']),**data))
    def __render_deskjs_content(self,yml,level=0,in_ul=False):
        if type(yml) is list:
            template_str=r'''<ul>
{% autoescape None %}
{{processed_content}}
</ul>'''
            cont = ""
            for item in yml:
                cont += self.__render_deskjs_content(item, level+1, True)
            return tornado.template.Template(template_str).generate(processed_content=cont)
        elif type(yml) is str or type(yml) is unicode:
            template_str=r''''''
            if in_ul:
                template_str=r'''<li><h%d>{{content}}</h%d></li>'''%(level+2,level+2)
            else:
                template_str=r'''<p>{{content}}</p>'''
            return tornado.template.Template(template_str).generate(content=yml)
        elif type(yml) is dict:
            retv = ""
            for k in yml:
                retv += self.__render_deskjs_content(k,level,in_ul)+\
                        self.__render_deskjs_content(yml[k],level)
            return retv
        else:
            raise RuntimeError(type(yml))

    def __addDeskjsSlide(self,slide_content):
        try:
            self.__deskjs_inited
        except:
            self.__deskjs_inited = True
            self.__deskjs_contents=""
        self.__deskjs_contents+=slide_content
        
def SlideGen(content):
    '''
    @summary: 从一个str类型，生成幻灯。
    @param content:(str) 输入
    '''
    gener = SlideGener(content)
    gener.process()
    return gener.gen_content()

if __name__ == '__main__':
    def DevTest():
        '''
        @summary: 开发时的测试函数。将Input.Slide读入，生成SlideShow
        '''
        result = ""
        with open("Input.yml","r") as f:
            all = f.read()
            result = SlideGen(all)
        
        with open("Result.html","w") as f:
            f.write(result)
            

    def Main():
        pass
    
    if DEBUG:
        DevTest()
    else:
        Main()