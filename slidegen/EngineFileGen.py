import os
import sys
import cssmin
import jsmin


if __name__ == '__main__':
    path = sys.argv[1]
    os.chdir(path)
    map={}
    for base,dir,files in os.walk('.'):
        for fn in files:
            file_path = base+'/'+fn
            file_content=None
            with open(file_path,'r') as f:
                file_content = f.read()
            map[file_path[2:] ]=file_content
    print '# *-* coding=utf-8'
    print "FILES={"
    for k in map:
        if k.find('test') != -1:
            pass
        elif k[-4:len(k)] =='.css':           # Minify css file
            print "r'''%s''':r'''%s''',"%(k,cssmin.cssmin(map[k]))
        elif k[-3:len(k)] == '.js':
            print "r'''%s''':r'''%s''',"%(k,jsmin.jsmin(map[k]))
        else:
            pass
    print "}"