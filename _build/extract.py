import re, html, json, os, sys, urllib.parse
root = sys.argv[1]
def rd(f): return open(os.path.join(root,f),encoding='utf-8',errors='ignore').read()
def clean(s):
    s=re.sub(r'(?s)<[^>]+>','',s); s=html.unescape(s).replace('\xa0',' ')
    return re.sub(r'\s+',' ',s).strip()
def fname(href): return urllib.parse.unquote(href)
idx = rd('caseindex.php.html')
cats=[]
for href,img in re.findall(r'<li><a href="(case\.php[^"]+)"><img src="([^"]+)"',rd('aboutus.php.html')):
    name = urllib.parse.unquote(href)[len('case.php?keywords='):-5]
    page = rd(fname(href))
    prods=[]
    for pid,thumb,title in re.findall(r'<dt>\s*<a href="showcase\.php%3Fid=(\d+)\.html"><img src="([^"]+)".*?<p class="intro">(.*?)</p>',page,re.S):
        prods.append(dict(id=int(pid),thumb=thumb,title=clean(title)))
    pager = re.findall(r'href="(case\.php[^"]*page[^"]*)"',page)
    cats.append(dict(name=name,img=img if img.startswith(('upfiles','images')) else '',products=prods,pager=pager))
detail={}
for f in os.listdir(root):
    m=re.match(r'showcase\.php\?id=(\d+)\.html$',f)
    if not m: continue
    s=rd(f)
    t=re.search(r'<div class="news_title">\s*<h1>(.*?)</h1>',s,re.S)
    body=re.search(r'<div class="news_ref">.*?</div>(.*?)</div>\s*</div>\s*</div>',s,re.S)
    b=body.group(1) if body else ''
    imgs=re.findall(r'<img[^>]+src="([^"]+)"',b)
    paras=[]
    for p in re.split(r'(?i)</p>|<br\s*/?>',b):
        c=clean(p)
        if c: paras.append(c)
    detail[int(m.group(1))]=dict(title=clean(t.group(1)) if t else '',imgs=imgs,paras=paras)
json.dump(dict(cats=cats,detail=detail),open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
for c in cats: print(c['name'],c['img'],len(c['products']),c['pager'][:3])
print(len(detail))
for k in list(detail)[:3]: print(k,detail[k])
