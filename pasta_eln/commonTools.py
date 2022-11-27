__all__ = ['commonTools']

# Don't look below, you will not understand this Python code :) I don't.

from js2py.pyjs import *
# setting scope
var = Scope( JS_BUILTINS )
set_global_object(var)

# Code follows:
var.registers(['getChildren', 'editString2Docs', 'ontology2Labels', 'hierarchy2String', 'uuidv4', 'fillDocBeforeCreate', 'camelCase'])
@Js
def PyJsHoisted_uuidv4_(this, arguments, var=var):
    var = Scope({'this':this, 'arguments':arguments}, var)
    var.registers([])
    @Js
    def PyJs_anonymous_0_(c, this, arguments, var=var):
        var = Scope({'c':c, 'this':this, 'arguments':arguments}, var)
        var.registers(['r', 'v', 'c'])
        var.put('r', ((var.get('Math').callprop('random')*Js(16.0))|Js(0.0)))
        var.put('v', (var.get('r') if PyJsStrictEq(var.get('c'),Js('x')) else (var.get('r')&(Js(3)|Js(8)))))
        return var.get('v').callprop('toString', Js(16.0))
    PyJs_anonymous_0_._set_name('anonymous')
    return Js('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx').callprop('replace', JsRegExp('/[x]/g'), PyJs_anonymous_0_)
PyJsHoisted_uuidv4_.func_name = 'uuidv4'
var.put('uuidv4', PyJsHoisted_uuidv4_)
@Js
def PyJsHoisted_fillDocBeforeCreate_(data, docType, this, arguments, var=var):
    var = Scope({'data':data, 'docType':docType, 'this':this, 'arguments':arguments}, var)
    var.registers(['initSpaces', 'i', 'line', 'otherTags', 'prefix', 'keys', 'data', 'docType', 'fields', 'protectedKeys', 'now', 'text', 'rating', 'prefixJ'])
    var.put('protectedKeys', Js([Js('comment'), Js('tags'), Js('image')]))
    if var.get('data').get('-type').neg():
        var.get('data').put('-type', Js([var.get('docType')]))
    if (PyJsStrictEq(var.get('data').get('-type').typeof(),Js('string')) or var.get('data').get('-type').instanceof(var.get('String'))):
        var.get('data').put('-type', var.get('data').get('-type').callprop('split', Js('/')))
    if var.get('data').get('_id').neg():
        var.put('prefix', (Js('x') if (var.get('docType').get('0')==Js('x')) else var.get('docType').get('0').get('0')))
        var.get('data').put('_id', ((var.get('prefix')+Js('-'))+var.get('uuidv4')()))
    var.put('now', var.get('Date').create())
    var.get('data').put('-date', var.get('now').callprop('toISOString'))
    if var.get('data').get('-branch').neg():
        var.get('data').put('-branch', Js([Js({'stack':Js([]),'path':var.get(u"null")})]))
    if var.get('data').get('comment').neg():
        var.get('data').put('comment', Js(''))
    if var.get('data').get('tags').neg():
        var.get('data').put('tags', Js([]))
    var.put('rating', var.get('data').get('comment').callprop('match', JsRegExp('/#\\d/')))
    if PyJsStrictEq(var.get('rating'),var.get(u"null")):
        var.put('rating', Js([]))
    var.put('otherTags', var.get('data').get('comment').callprop('match', JsRegExp('/(^|\\s)#{1}[a-zA-Z][\\w]+/g')))
    if PyJsStrictEq(var.get('otherTags'),var.get(u"null")):
        var.put('otherTags', Js([]))
    var.get('data').put('tags', var.get('rating').callprop('concat', var.get('data').get('tags')).callprop('concat', var.get('otherTags')))
    var.get('data').put('comment', var.get('data').get('comment').callprop('replace', JsRegExp('/(^|\\s)#{1}[\\w]+/g'), Js(' ')))
    var.put('fields', var.get('data').get('comment').callprop('match', JsRegExp('/:[\\S]+:[\\S]+:/g')))
    if (var.get('fields')!=var.get(u"null")):
        @Js
        def PyJs_anonymous_1_(item, this, arguments, var=var):
            var = Scope({'item':item, 'this':this, 'arguments':arguments}, var)
            var.registers(['aList', 'item'])
            var.put('aList', var.get('item').callprop('split', Js(':')))
            if var.get('data').get(var.get('aList').get('1')):
                return var.get('undefined')
            if var.get('isNaN')(var.get('aList').get('2')):
                return var.get('data').put(var.get('aList').get('1'), var.get('aList').get('2'))
            else:
                return var.get('data').put(var.get('aList').get('1'), (+var.get('aList').get('2')))
        PyJs_anonymous_1_._set_name('anonymous')
        var.get('fields').callprop('map', PyJs_anonymous_1_)
    var.get('data').put('comment', var.get('data').get('comment').callprop('replace', JsRegExp('/:[\\S]+:[\\S]+:/g'), Js('')))
    var.put('text', var.get('data').get('comment').callprop('split', Js('\n')))
    var.get('data').put('comment', Js(''))
    #for JS loop
    var.put('i', Js(0.0))
    while (var.get('i')<var.get('text').get('length')):
        try:
            var.put('line', var.get('text').get(var.get('i')))
            var.put('initSpaces', var.get('line').callprop('search', JsRegExp('/\\S|$/')))
            #for JS loop
            var.put('prefixJ', Js(''))
            while (var.get('prefixJ').get('length')<(var.get('Math').callprop('round', (var.get('initSpaces')/Js(2.0)))*Js(2.0))):
                try:
                    pass
                finally:
                        var.put('prefixJ', Js(' '), '+')
            var.get('data').put('comment', ((var.get('prefixJ')+var.get('line').callprop('trim'))+Js('\n')), '+')
        finally:
                (var.put('i',Js(var.get('i').to_number())+Js(1))-Js(1))
    var.get('data').put('comment', var.get('data').get('comment').callprop('substring', Js(0.0), (var.get('data').get('comment').get('length')-Js(1.0))))
    if (PyJsStrictEq(var.get('data').get('tags').typeof(),Js('string')) or var.get('data').get('tags').instanceof(var.get('String'))):
        var.get('data').put('tags', var.get('data').get('tags').callprop('split', Js(' ')))
    @Js
    def PyJs_anonymous_2_(v, this, arguments, var=var):
        var = Scope({'v':v, 'this':this, 'arguments':arguments}, var)
        var.registers(['v'])
        return var.get('v').callprop('trim')
    PyJs_anonymous_2_._set_name('anonymous')
    var.get('data').put('tags', var.get('data').get('tags').callprop('map', PyJs_anonymous_2_))
    if PyJsStrictEq(var.get('data').get('-type').get('0'),Js('sample')):
        if var.get('data').get('qrCode').neg():
            var.get('data').put('qrCode', Js([]))
        if (PyJsStrictEq(var.get('data').get('qrCode').typeof(),Js('string')) or var.get('data').get('qrCode').instanceof(var.get('String'))):
            var.get('data').put('qrCode', var.get('data').get('qrCode').callprop('split', Js(' ')))
    if PyJsStrictEq(var.get('data').get('-type').get('0'),Js('measurement')):
        if var.get('data').get('image').neg():
            var.get('data').put('image', Js(''))
        if var.get('data').get('shasum').neg():
            var.get('data').put('shasum', Js(''))
    var.put('keys', var.get('Object').callprop('keys', var.get('data')))
    @Js
    def PyJs_anonymous_3_(key, this, arguments, var=var):
        var = Scope({'key':key, 'this':this, 'arguments':arguments}, var)
        var.registers(['key'])
        if (PyJsStrictEq(var.get('data').get(var.get('key')).typeof(),Js('string')) or var.get('data').get(var.get('key')).instanceof(var.get('String'))):
            if ((var.get('data').get(var.get('key'))==Js('')) and (var.get('protectedKeys').callprop('indexOf', var.get('key'))==(-Js(1.0)))):
                var.get('data').delete(var.get('key'))
            else:
                var.get('data').put(var.get('key'), var.get('data').get(var.get('key')).callprop('trim'))
    PyJs_anonymous_3_._set_name('anonymous')
    var.get('keys').callprop('map', PyJs_anonymous_3_)
    return var.get('data')
PyJsHoisted_fillDocBeforeCreate_.func_name = 'fillDocBeforeCreate'
var.put('fillDocBeforeCreate', PyJsHoisted_fillDocBeforeCreate_)
@Js
def PyJsHoisted_ontology2Labels_(ontology, tableFormat, this, arguments, var=var):
    var = Scope({'ontology':ontology, 'tableFormat':tableFormat, 'this':this, 'arguments':arguments}, var)
    var.registers(['dataDict', 'ontology', 'hierarchyDict', 'tableFormat'])
    var.put('dataDict', Js({}))
    var.put('hierarchyDict', Js({}))
    @Js
    def PyJs_anonymous_4_(key, this, arguments, var=var):
        var = Scope({'key':key, 'this':this, 'arguments':arguments}, var)
        var.registers(['key', 'label'])
        if ((var.get('key')==Js('_id')) or (var.get('key')==Js('_rev'))):
            return var.get('undefined')
        var.put('label', var.get(u"null"))
        if (var.get('tableFormat').contains(var.get('key')) and var.get('tableFormat').get(var.get('key')).contains(Js('-label-'))):
            var.put('label', var.get('tableFormat').get(var.get('key')).get('-label-'))
        else:
            if (var.get('key').get('0')==Js('x')):
                var.put('label', Js([Js('Projects'), Js('Tasks'), Js('Subtasks'), Js('Subsubtasks')]).get(var.get('key').get('1')))
            else:
                var.put('label', ((var.get('key').get('0').callprop('toUpperCase')+var.get('key').callprop('slice', Js(1.0)))+Js('s')))
        if (var.get('key').get('0')==Js('x')):
            var.get('hierarchyDict').put(var.get('key'), var.get('label'))
        else:
            var.get('dataDict').put(var.get('key'), var.get('label'))
        return var.get('undefined')
    PyJs_anonymous_4_._set_name('anonymous')
    var.get('Object').callprop('keys', var.get('ontology')).callprop('map', PyJs_anonymous_4_)
    return Js({'dataDict':var.get('dataDict'),'hierarchyDict':var.get('hierarchyDict')})
PyJsHoisted_ontology2Labels_.func_name = 'ontology2Labels'
var.put('ontology2Labels', PyJsHoisted_ontology2Labels_)
@Js
def PyJsHoisted_hierarchy2String_(data, addID, callback, detail, magicTags, this, arguments, var=var):
    var = Scope({'data':data, 'addID':addID, 'callback':callback, 'detail':detail, 'magicTags':magicTags, 'this':this, 'arguments':arguments}, var)
    var.registers(['dataList', 'callback', 'addID', 'value', 'i', 'id', 'keys', 'data', 'key', 'hierarchyIDs', 'childNum', 'detail', 'j', 'outString', 'magicTags', 'hierString', 'compare'])
    @Js
    def PyJsHoisted_compare_(a, b, this, arguments, var=var):
        var = Scope({'a':a, 'b':b, 'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'a'])
        if (var.get('a').get('hierarchy')>var.get('b').get('hierarchy')):
            return Js(1.0)
        else:
            return (-Js(1.0))
    PyJsHoisted_compare_.func_name = 'compare'
    var.put('compare', PyJsHoisted_compare_)
    var.put('dataList', Js([]))
    var.put('keys', var.get('Object').callprop('keys', var.get('data')))
    var.put('hierString', var.get(u"null"))
    #for JS loop
    var.put('i', Js(0.0))
    while (var.get('i')<var.get('keys').get('length')):
        try:
            var.put('key', var.get('keys').get(var.get('i')))
            var.put('value', var.get('data').get(var.get('key')))
            if PyJsStrictEq(var.get('value').get('0'),var.get('key')):
                var.put('hierString', var.get('key'))
            else:
                var.put('hierarchyIDs', var.get('value').get('0').callprop('split', Js(' ')))
                var.put('hierString', var.get('hierarchyIDs').get('0'))
                #for JS loop
                var.put('j', Js(1.0))
                while (var.get('j')<var.get('hierarchyIDs').get('length')):
                    try:
                        var.put('id', var.get('hierarchyIDs').get(var.get('j')))
                        var.put('childNum', Js(0.0))
                        if var.get('data').contains(var.get('id')):
                            var.put('childNum', var.get('data').get(var.get('id')).get('1'))
                        if (var.get('childNum')>Js(9999.0)):
                            var.get('console').callprop('log', (Js('**ERROR** commonTools:ChildNUM>9999 **ERROR** ')+var.get('key')))
                        var.put('hierString', (((Js(' ')+(Js('00')+var.get('childNum')).callprop('substr', (-Js(3.0))))+Js(' '))+var.get('id')), '+')
                    finally:
                            (var.put('j',Js(var.get('j').to_number())+Js(1))-Js(1))
            var.get('dataList').callprop('push', Js({'hierarchy':var.get('hierString'),'label':var.get('value').callprop('slice', Js(2.0))}))
        finally:
                (var.put('i',Js(var.get('i').to_number())+Js(1))-Js(1))
    pass
    var.get('dataList').callprop('sort', var.get('compare'))
    @Js
    def PyJs_anonymous_5_(item, this, arguments, var=var):
        var = Scope({'item':item, 'this':this, 'arguments':arguments}, var)
        var.registers(['i', 'doc', 'prefix', 'partString', 'hierarchyArray', 'spaces', 'i3', 'i1', 'docID', 'item', 'i2'])
        var.put('hierarchyArray', var.get('item').get('hierarchy').callprop('split', Js(' ')))
        var.put('spaces', ((var.get('hierarchyArray').get('length')/Js(2.0))-Js(0.5)))
        #for JS loop
        var.put('prefix', Js(''))
        while (var.get('prefix').get('length')<=var.get('spaces')):
            try:
                pass
            finally:
                    var.put('prefix', Js('*'), '+')
        if PyJsStrictEq(var.get('addID'),Js(True)):
            var.put('partString', var.get('item').get('label').get('1'))
            var.put('docID', var.get('hierarchyArray').get((var.get('hierarchyArray').get('length')-Js(1.0))))
            var.put('partString', (Js('||')+var.get('docID')), '+')
            if PyJsStrictEq(var.get('callback',throw=False).typeof(),Js('function')):
                var.put('doc', var.get('callback')(var.get('docID')))
                if PyJsStrictEq(var.get('detail'),Js('all')):
                    #for JS loop
                    var.put('i', Js(0.0))
                    while (var.get('i')<var.get('doc').get('-branch').get('length')):
                        try:
                            var.put('partString', (Js('\nPath: ')+var.get('doc').get('-branch').get(var.get('i')).get('path')), '+')
                        finally:
                                (var.put('i',Js(var.get('i').to_number())+Js(1))-Js(1))
                    var.put('partString', Js('\nInheritance: '), '+')
                    #for JS loop
                    var.put('i1', Js(0.0))
                    while (var.get('i1')<var.get('doc').get('-branch').get('length')):
                        try:
                            var.put('partString', (var.get('doc').get('-branch').get(var.get('i1')).get('stack')+Js(' ')), '+')
                        finally:
                                (var.put('i1',Js(var.get('i1').to_number())+Js(1))-Js(1))
                if (var.get('doc').get('-type')==Js([Js('x'), Js('project')])):
                    var.put('partString', (Js('\nObjective: ')+var.get('doc').get('objective')), '+')
                #for JS loop
                var.put('i2', Js(0.0))
                while (var.get('i2')<var.get('magicTags').get('length')):
                    try:
                        if (var.get('doc').get('tags').callprop('indexOf', (Js('#')+var.get('magicTags').get(var.get('i2'))))>(-Js(1.0))):
                            var.put('prefix', ((var.get('prefix')+Js(' '))+var.get('magicTags').get(var.get('i2'))))
                            #for JS loop
                            var.put('i3', Js(0.0))
                            while (var.get('i3')<var.get('doc').get('tags').get('length')):
                                try:
                                    if PyJsStrictEq(var.get('doc').get('tags').get(var.get('i3')),(Js('#')+var.get('magicTags').get(var.get('i2')))):
                                        var.get('doc').get('tags').callprop('splice', var.get('i'), Js(1.0))
                                        (var.put('i',Js(var.get('i').to_number())-Js(1))+Js(1))
                                finally:
                                        (var.put('i3',Js(var.get('i3').to_number())+Js(1))-Js(1))
                    finally:
                            (var.put('i2',Js(var.get('i2').to_number())+Js(1))-Js(1))
                var.put('partString', (((Js('\nTags: ')+var.get('doc').get('tags').callprop('join', Js(' ')))+Js('\n'))+var.get('doc').get('comment')), '+')
            var.put('partString', ((var.get('prefix')+Js(' '))+var.get('partString')))
        else:
            var.put('partString', ((((var.get('prefix')+Js(' '))+var.get('item').get('label').get('0'))+Js(': '))+var.get('item').get('label').get('1')))
        return var.get('partString')
    PyJs_anonymous_5_._set_name('anonymous')
    var.put('outString', var.get('dataList').callprop('map', PyJs_anonymous_5_))
    return var.get('outString').callprop('join', Js('\n'))
PyJsHoisted_hierarchy2String_.func_name = 'hierarchy2String'
var.put('hierarchy2String', PyJsHoisted_hierarchy2String_)
@Js
def PyJsHoisted_editString2Docs_(text, magicTags, this, arguments, var=var):
    var = Scope({'text':text, 'magicTags':magicTags, 'this':this, 'arguments':arguments}, var)
    var.registers(['tags', 'i', 'line', 'docType', 'docI', 'title', 'j', 'magicTags', 'docs', 'text', 'comment', 'docID', 'parts', 'objective'])
    var.put('docs', Js([]))
    var.put('objective', var.get(u"null"))
    var.put('tags', var.get(u"null"))
    var.put('comment', var.get(u"null"))
    var.put('title', Js(''))
    var.put('docID', Js(''))
    var.put('docType', Js(''))
    var.put('text', var.get('text').callprop('split', Js('\n')))
    #for JS loop
    var.put('i', Js(0.0))
    while (var.get('i')<var.get('text').get('length')):
        try:
            var.put('line', var.get('text').get(var.get('i')))
            def PyJs_LONG_6_(var=var):
                return ((((PyJsStrictEq(var.get('line').callprop('substring', Js(0.0), Js(2.0)),Js('* ')) or PyJsStrictEq(var.get('line').callprop('substring', Js(0.0), Js(3.0)),Js('** '))) or PyJsStrictEq(var.get('line').callprop('substring', Js(0.0), Js(4.0)),Js('*** '))) or PyJsStrictEq(var.get('line').callprop('substring', Js(0.0), Js(5.0)),Js('**** '))) or PyJsStrictEq(var.get('line').callprop('substring', Js(0.0), Js(6.0)),Js('***** ')))
            if (PyJs_LONG_6_() or PyJsStrictEq(var.get('line').callprop('substring', Js(0.0), Js(7.0)),Js('****** '))):
                if var.get('comment'):
                    var.put('comment', var.get('comment').callprop('trim'))
                var.put('docI', Js({'-name':var.get('title'),'tags':var.get('tags'),'comment':var.get('comment'),'_id':var.get('docID'),'-type':var.get('docType')}))
                if var.get('objective'):
                    var.get('docI').put('objective', var.get('objective'))
                if ((var.get('title')==Js('-delete-')) and (var.get('docID')!=Js(''))):
                    var.get('docI').put('edit', Js('-delete-'))
                else:
                    if (var.get('docID')==Js('')):
                        var.get('docI').put('edit', Js('-new-'))
                    else:
                        var.get('docI').put('edit', Js('-edit-'))
                if ((var.get('docID')!=Js('')) or (var.get('title')!=Js(''))):
                    var.get('docs').callprop('push', var.get('docI'))
                var.put('objective', var.get(u"null"))
                var.put('tags', var.get(u"null"))
                var.put('comment', var.get(u"null"))
                var.put('title', Js(''))
                var.put('docID', Js(''))
                var.put('docType', Js(''))
                var.put('parts', var.get('line').callprop('split', Js('||')))
                var.put('title', var.get('parts').get('0').callprop('split', Js(' ')).callprop('slice', Js(1.0)).callprop('join', Js(' ')).callprop('trim'))
                #for JS loop
                var.put('j', (var.get('magicTags').get('length')-Js(1.0)))
                while (var.get('j')>=Js(0.0)):
                    try:
                        if PyJsStrictEq(var.get('title').callprop('substring', Js(0.0), Js(4.0)),var.get('magicTags').get(var.get('j'))):
                            var.put('title', var.get('title').callprop('slice', (var.get('magicTags').get(var.get('j')).get('length')+Js(1.0))))
                            var.put('tags', ((Js('#')+var.get('magicTags').get(var.get('j')))+Js(' ')), '+')
                    finally:
                            (var.put('j',Js(var.get('j').to_number())-Js(1))+Js(1))
                if var.get('tags'):
                    var.put('tags', var.get('tags').callprop('trim'))
                if (var.get('parts').get('length')>Js(1.0)):
                    var.put('docID', var.get('parts').get((var.get('parts').get('length')-Js(1.0))))
                var.put('docType', (var.get('line').callprop('split', Js(' ')).get('0').get('length')-Js(1.0)))
            else:
                if PyJsStrictEq(var.get('line').callprop('substring', Js(0.0), Js(10.0)),Js('Objective:')):
                    var.put('objective', var.get('line').callprop('substring', Js(10.0), var.get('line').get('length')).callprop('trim'))
                else:
                    if PyJsStrictEq(var.get('line').callprop('substring', Js(0.0), Js(5.0)),Js('Tags:')):
                        var.put('tags', (var.get('line').callprop('substring', Js(5.0), var.get('line').get('length')).callprop('trim') if PyJsStrictEq(var.get('tags'),var.get(u"null")) else (var.get('tags')+var.get('line').callprop('substring', Js(5.0), var.get('line').get('length')).callprop('trim'))))
                    else:
                        if JsRegExp('/\\|\\|\\w-/').callprop('test', var.get('line')).neg():
                            var.put('comment', ((var.get('line')+Js('\n')) if PyJsStrictEq(var.get('comment'),var.get(u"null")) else ((var.get('comment')+var.get('line'))+Js('\n'))))
        finally:
                (var.put('i',Js(var.get('i').to_number())+Js(1))-Js(1))
    if var.get('comment'):
        var.put('comment', var.get('comment').callprop('trim'))
    var.put('docI', Js({'-name':var.get('title'),'tags':var.get('tags'),'comment':var.get('comment'),'_id':var.get('docID'),'-type':var.get('docType')}))
    if var.get('objective'):
        var.get('docI').put('objective', var.get('objective'))
    if ((var.get('title')==Js('-delete-')) and (var.get('docID')!=Js(''))):
        var.get('docI').put('edit', Js('-delete-'))
    else:
        if (var.get('docID')==Js('')):
            var.get('docI').put('edit', Js('-new-'))
        else:
            var.get('docI').put('edit', Js('-edit-'))
    var.get('docs').callprop('push', var.get('docI'))
    return var.get('docs')
PyJsHoisted_editString2Docs_.func_name = 'editString2Docs'
var.put('editString2Docs', PyJsHoisted_editString2Docs_)
@Js
def PyJsHoisted_getChildren_(data, docID, this, arguments, var=var):
    var = Scope({'data':data, 'docID':docID, 'this':this, 'arguments':arguments}, var)
    var.registers(['names', 'i', 'items', 'data', 'saveLine', 'lines', 'ids', 'nStars', 'numStarsParent', 'docID'])
    var.put('names', Js([]))
    var.put('ids', Js([]))
    var.put('saveLine', Js(False))
    var.put('numStarsParent', (-Js(1.0)))
    var.put('lines', var.get('data').callprop('split', Js('\n')))
    #for JS loop
    var.put('i', Js(0.0))
    while (var.get('i')<var.get('lines').get('length')):
        try:
            var.put('items', var.get('lines').get(var.get('i')).callprop('split', Js('||')))
            if var.get('saveLine'):
                var.put('nStars', var.get('items').get('0').callprop('split', Js(' ')).get('0').get('length'))
                if PyJsStrictEq(var.get('nStars'),var.get('numStarsParent')):
                    break
                if PyJsStrictEq(var.get('nStars'),(var.get('numStarsParent')+Js(1.0))):
                    var.get('ids').callprop('push', var.get('items').get('1'))
                    var.get('names').callprop('push', var.get('items').get('0').callprop('substring', (var.get('numStarsParent')+Js(2.0))))
            if PyJsStrictEq(var.get('items').get('1'),var.get('docID')):
                if PyJsStrictEq(var.get('items').get('0').get('0'),Js('*')):
                    var.put('numStarsParent', var.get('items').get('0').callprop('split', Js(' ')).get('length'))
                else:
                    var.put('numStarsParent', Js(0.0))
                var.put('saveLine', Js(True))
        finally:
                (var.put('i',Js(var.get('i').to_number())+Js(1))-Js(1))
    return Js({'names':var.get('names'),'ids':var.get('ids')})
PyJsHoisted_getChildren_.func_name = 'getChildren'
var.put('getChildren', PyJsHoisted_getChildren_)
@Js
def PyJsHoisted_camelCase_(str, this, arguments, var=var):
    var = Scope({'str':str, 'this':this, 'arguments':arguments}, var)
    var.registers(['outString', 'str'])
    @Js
    def PyJs_anonymous_7_(match, this, arguments, var=var):
        var = Scope({'match':match, 'this':this, 'arguments':arguments}, var)
        var.registers(['match'])
        if JsRegExp('/\\s+/').callprop('test', var.get('match')):
            return Js('')
        return var.get('match').callprop('toUpperCase')
    PyJs_anonymous_7_._set_name('anonymous')
    var.put('outString', var.get('str').callprop('replace', JsRegExp('/(?:^\\w|[A-Z]|\\b\\w|\\s+)/g'), PyJs_anonymous_7_))
    var.put('outString', var.get('outString').callprop('replace', JsRegExp('/\\W/g'), Js('')))
    return var.get('outString')
PyJsHoisted_camelCase_.func_name = 'camelCase'
var.put('camelCase', PyJsHoisted_camelCase_)
pass
pass
pass
pass
pass
pass
pass
pass


# Add lib to the module scope
commonTools = var.to_python()
# HASH: e0cd78426e5deec90656155484cef6df4e392472