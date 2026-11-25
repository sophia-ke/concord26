#!/usr/bin/env python3
"""Generate the bilingual Concord 26 site (Chinese at the root, English in en/).
Usage: python3 -I build.py <site_root>"""
import json, os, re, sys, html
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import i18n_en as EN

ROOT = sys.argv[1]
DATA = json.load(open(os.path.join(HERE, 'data_zh.json'), encoding='utf-8'))
e = lambda s: html.escape(s or '', quote=True)

# ---------- content model ----------
CAT_INFO = {  # order on the site, short description, brand line (from the original catalogue)
    '全光纤一体化手术室': ('数字一体化智慧手术室整体方案：影像、显示、示教与远程手术云平台集成于一体。', '整体方案'),
    '手术无影灯、医用吊塔': ('AMI 与 SYSTEM TWO LED 手术无影灯、检查灯，以及 Navigator / SUPPORT 多功能医用吊塔。', 'Medical Illumination'),
    '圣奥手术头灯': ('氙光源与 LED 手术头灯，可选配全高清摄像系统，记录主刀视野。', 'Sunoptic 圣奥'),
    '牵开器': ('OMNI-TRACT 奥美系列专科牵开器：腔镜、骨科、泌尿、小儿、血管、移植与普外。', 'OMNI-TRACT 奥美'),
    '手术牵开器': ('腹部手术牵开器，覆盖普外、泌尿、小儿、胸心血管与妇产科手术。', 'Integra'),
    '输液恒温仪': ('暖宝快速输液恒温仪：术中输液即时加温，双温控传感器精确控温。', '暖宝'),
    'UV24消毒机': ('UV24 手术室环境消毒设备，守护洁净手术环境。', 'UV24'),
}
ORDER = list(CAT_INFO)
cats = {c['name']: c for c in DATA['cats']}
CATS = [dict(name=n, logo=cats[n]['img'], products=cats[n]['products']) for n in ORDER]
DET = {int(k): v for k, v in DATA['detail'].items()}

def split_feats(paras):
    """-> (model, [(kind,text)]) ; kind 'sub' for heading-like lines."""
    model, out = '', []
    for p in paras:
        p = p.strip().strip('·•').strip()
        if not p: continue
        m = re.match(r'^型号[：:]\s*(.+)$', p)
        if m: model = m.group(1); continue
        parts = re.split(r'(?<=[^：])(?=(?:普外科|泌尿外科|小儿外科|胸心血管外科|妇产科)：)', p)
        for q in parts:
            q = q.strip()
            if not q: continue
            if re.match(r'^(性能特点|.*的优势)[：:]?$', q): out.append(('sub', q.rstrip('：:'))); continue
            q = re.sub(r'^\d+[、.．]\s*', '', q)
            out.append(('li', q))
    return model, out

PRODUCTS = []
for c in CATS:
    for p in c['products']:
        d = DET[p['id']]
        model, feats = split_feats(d['paras'])
        imgs = [p['thumb']] + [i for i in d['imgs'] if i != p['thumb']]
        PRODUCTS.append(dict(id=p['id'], title=d['title'] or p['title'], cat=c['name'], thumb=p['thumb'],
                             imgs=imgs, model=model, feats=feats))
BY_CAT = {c['name']: [p for p in PRODUCTS if p['cat'] == c['name']] for c in CATS}

def enc(fname):  # file name -> href (the "?" in mirrored names must be escaped)
    return quote(fname, safe='=.')
SLUG = {'全光纤一体化手术室': 'integrated-or', '手术无影灯、医用吊塔': 'lights-pendants', '圣奥手术头灯': 'headlights',
        '牵开器': 'retractors', '手术牵开器': 'abdominal-retractors', '输液恒温仪': 'fluid-warmers', 'UV24消毒机': 'uv24'}
cat_file = lambda n: 'category-%s.html' % SLUG[n]
prod_file = lambda pid: 'product-%d.html' % pid
cat_href = lambda n: enc(cat_file(n))
prod_href = lambda pid: enc(prod_file(pid))

# ---------- icons ----------
ARROW = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" stroke="currentColor" stroke-width="1.4"/></svg>'
DOWN = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 2v11M3.5 9 8 13.5 12.5 9" stroke="currentColor" stroke-width="1.4"/></svg>'
SEARCH = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.4"/><path d="m11 11 3.5 3.5" stroke="currentColor" stroke-width="1.4"/></svg>'
GLOBE = ('<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="7.5" stroke="currentColor" stroke-width="1.3"/>'
         '<path d="M2.5 10h15M10 2.5c2.2 2.1 3.3 4.6 3.3 7.5s-1.1 5.4-3.3 7.5c-2.2-2.1-3.3-4.6-3.3-7.5S7.8 4.6 10 2.5Z" stroke="currentColor" stroke-width="1.3"/></svg>')
CUR = ' aria-current="page"'
HERO_IMG = 'upfiles/20210126073818578.jpg'

# ---------- auto language detection (runs in <head>, before paint) ----------
# Order: explicit choice (switcher or ?lang=) > cached auto result > browser language > IP country.
# The IP lookup only happens for visitors whose browser is not set to Chinese.
DETECT = r'''<script>
(function(){var L="%(lang)s",ALT="%(alt)s",K="c26-lang",A="c26-auto";
function go(t){if(t!==L)location.replace(ALT+location.hash)}
try{var m=location.search.match(/[?&]lang=(zh|en)\b/);if(m){localStorage.setItem(K,m[1]);go(m[1]);return}
var p=localStorage.getItem(K);if(p){go(p);return}
var a=localStorage.getItem(A);if(a){go(a);return}
if(/bot|crawl|spider|slurp|preview/i.test(navigator.userAgent))return;
var b=((navigator.languages&&navigator.languages[0])||navigator.language||"").toLowerCase();
if(b.indexOf("zh")===0){localStorage.setItem(A,"zh");go("zh");return}
var done=false,fin=function(t){if(done)return;done=true;localStorage.setItem(A,t);go(t)};
setTimeout(function(){fin("en")},1500);
fetch("https://api.country.is/").then(function(r){return r.json()}).then(function(d){
fin(/^(CN|HK|MO|TW)$/.test(d&&d.country||"")?"zh":"en")}).catch(function(){fin("en")});
}catch(x){}})();
</script>'''


def build(L):
    zh = L == 'zh'
    P = '' if zh else '../'                     # prefix for shared assets / images
    OUT = ROOT if zh else os.path.join(ROOT, 'en')
    os.makedirs(OUT, exist_ok=True)
    t = lambda a, b: a if zh else b
    tr = (lambda s: s) if zh else (lambda s: EN.T[s])
    cname = lambda n: n if zh else EN.CATS[n]['name']
    cdesc = lambda n: CAT_INFO[n][0] if zh else EN.CATS[n]['desc']
    cbrand = lambda n: CAT_INFO[n][1] if zh else EN.CATS[n]['brand']
    img = lambda s: P + s
    psum = lambda p: next((tr(x) for k, x in p['feats'] if k == 'li'), '')
    nprod = lambda n: (f'{n} 件产品' if zh else f'{n} product' + ('' if n == 1 else 's'))

    NAV = [('index.html', t('首页', 'Home'), 'home'), ('about.html', t('关于康迎', 'About'), 'about'),
           ('products.html', t('产品中心', 'Products'), 'products'), ('news.html', t('新闻中心', 'News'), 'news'),
           ('contact.html', t('联系我们', 'Contact'), 'contact')]

    def eyebrow(n, label):
        return f'<p class="eyebrow"><span class="n">{n}</span><i></i><span>{e(label)}</span></p>'

    def lang_links(fname):
        zh_href = enc(fname) if zh else '../' + enc(fname)
        en_href = 'en/' + enc(fname) if zh else enc(fname)
        return zh_href, en_href

    def page(fname, title, active, body, desc=None, over=False):
        desc = desc or t('上海康迎医疗器械有限公司 — 数字化智慧手术室系统与设备',
                         'Concord Medical, Shanghai — digital integrated operating room systems and equipment since 2002.')
        zh_href, en_href = lang_links(fname)
        alt = en_href if zh else zh_href
        nav = ''.join(f'<a href="{h}"{CUR if k == active else ""}>{x}</a>' for h, x, k in NAV)
        mnav = ''.join(f'<li><a href="{h}"><span>{i+1:02d}</span>{x}</a></li>' for i, (h, x, k) in enumerate(NAV))
        foot_products = ''.join(f'<li><a href="{cat_href(c["name"])}">{e(cname(c["name"]))}</a></li>' for c in CATS[:6])
        logo_alt = 'CONCORD 康迎医疗'
        lang = f'''<div class="lang">
      <button class="lang-btn" aria-haspopup="true" aria-expanded="false" aria-label="{t('切换语言', 'Change language')}">{GLOBE}<span>{t('中文', 'EN')}</span></button>
      <ul class="lang-menu">
        <li><a href="{zh_href}" data-setlang="zh" lang="zh-CN"{CUR if zh else ''}>简体中文</a></li>
        <li><a href="{en_href}" data-setlang="en" lang="en"{'' if zh else CUR}>English</a></li>
      </ul></div>'''
        return f'''<!DOCTYPE html>
<html lang="{t('zh-CN', 'en')}" class="no-js lang-{L}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{DETECT % dict(lang=L, alt=alt)}
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#102733">
<link rel="alternate" hreflang="zh-CN" href="{zh_href}">
<link rel="alternate" hreflang="en" href="{en_href}">
<link rel="alternate" hreflang="x-default" href="{en_href}">
<link rel="icon" type="image/svg+xml" href="{P}assets/logo-color.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500&family=Manrope:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{P}assets/c26.css">
</head>
<body>
<header class="hdr{' is-over' if over else ' is-solid'}">
  <div class="wrap">
    <a class="logo" href="index.html" aria-label="{t('康迎医疗 首页', 'Concord Medical home')}"><img class="lg-c" src="{P}assets/logo-color.svg" alt="{logo_alt}" width="164" height="36"><img class="lg-w" src="{P}assets/logo-white.png" alt="" width="163" height="36"></a>
    <div class="right">
      <nav class="nav" aria-label="{t('主导航', 'Main')}">{nav}</nav>
      {lang}
      <button class="burger" data-menu aria-label="{t('打开菜单', 'Open menu')}" aria-expanded="false"><span></span></button>
    </div>
  </div>
</header>
<div class="menu" role="dialog" aria-label="{t('菜单', 'Menu')}">
  <div class="wrap top"><a class="logo" href="index.html"><img class="lg-w" src="{P}assets/logo-white.png" alt="{logo_alt}" width="163" height="36"></a><button class="close" data-menu aria-label="{t('关闭菜单', 'Close menu')}"></button></div>
  <div class="wrap" style="display:flex;flex-direction:column;flex:1"><ol>{mnav}</ol>
  </div>
</div>
<main>
{body}
</main>
<footer class="ftr">
  <div class="wrap">
    <a class="logo" href="index.html"><img class="lg-w" src="{P}assets/logo-white.png" alt="{logo_alt}" width="181" height="40"></a>
    <p class="tag">{t('卓越，源自专业。为医院提供数字一体化智慧手术室与远程手术云平台整体解决方案。',
                    'Excellence, born of expertise. Complete digital integrated operating rooms and remote-surgery cloud platforms for hospitals.')}</p>
    <div class="cols">
      <div><h4>{t('产品中心', 'Products')}</h4><ul>{foot_products}</ul></div>
      <div><h4>{t('公司', 'Company')}</h4><ul><li><a href="about.html">{t('关于康迎', 'About us')}</a></li><li><a href="news.html">{t('新闻中心', 'News')}</a></li><li><a href="products.html">{t('全部产品', 'All products')}</a></li><li><a href="contact.html">{t('联系我们', 'Contact')}</a></li></ul></div>
      <div><h4>{t('服务网络', 'Service network')}</h4><ul><li>{t('上海 · 总部', 'Shanghai · Headquarters')}</li><li>{t('北京 · 办事机构', 'Beijing · Office')}</li><li>{t('广州 · 办事机构', 'Guangzhou · Office')}</li><li>{t('覆盖全国 31 个省市', '31 provinces across China')}</li></ul></div>
      <div><h4>{t('联系', 'Contact')}</h4><ul><li><a href="tel:+862152353552">{t('021-52353552', '+86 21-52353552')}</a></li><li>{t('传真 021-52356619', 'Fax +86 21-52356619')}</li><li><a href="mailto:marketing@concordmed.cn">marketing@concordmed.cn</a></li><li>{ADDR[L]}</li></ul></div>
    </div>
    <div class="base mono"><span>© 2002–2026 {t('上海康迎医疗器械有限公司', 'Shanghai Concord Medical Equipment Co., Ltd.')}</span><span><a href="https://beian.miit.gov.cn" target="_blank" rel="noopener noreferrer">沪ICP备12029303号-1</a> · <a href="{alt}" data-setlang="{t('en', 'zh')}">{t('English', '中文')}</a></span></div>
  </div>
</footer>
<script src="{P}assets/c26.js"></script>
</body>
</html>
'''

    def phead(crumbs, n, label, title_html, lead):
        cr = '<i>/</i>'.join(f'<a href="{h}">{e(x)}</a>' if h else f'<span>{e(x)}</span>' for h, x in crumbs)
        return f'''<section class="phead"><div class="wrap">
  <nav class="crumbs mono" aria-label="{t('面包屑', 'Breadcrumb')}">{cr}</nav>
  {eyebrow(n, label)}
  <div class="row"><h1 class="h1 rv">{title_html}</h1><p class="lead rv d1">{lead}</p></div>
</div></section>'''

    def pcard(p, i=0):
        s = psum(p)
        q = ' '.join([tr(p['title']), cname(p['cat']), tr(p['model']) if p['model'] else '', s])
        return f'''<a class="pcard rv d{i%3}" href="{prod_href(p['id'])}" data-cat="{e(p['cat'])}" data-q="{e(q)}">
  <div class="im"><img src="{e(img(p['thumb']))}" alt="{e(tr(p['title']))}" loading="lazy"></div>
  <div class="tx"><span class="mono">{e(cname(p['cat']))}</span><h3>{e(tr(p['title']))}</h3><p>{e(s or cdesc(p['cat']))}</p>
  <span class="more">{t('查看详情', 'View details')} {ARROW}</span></div></a>'''

    def cta_band():
        return f'''<section class="sec surf tight"><div class="wrap cta">
  <div>{eyebrow('—', t('联系康迎', 'Talk to us'))}<h2 class="h2 rv">{t('为您的手术室，<br><span class="muted">找到合适的方案。</span>', 'The right solution<br><span class="muted">for your operating room.</span>')}</h2></div>
  <div class="acts rv d1"><a class="btn btn-ink" href="contact.html">{t('联系我们', 'Contact us')} {ARROW}</a><a class="btn btn-line" href="tel:+862152353552">{t('021-52353552', '+86 21-52353552')}</a></div>
</div></section>'''

    def stats():
        return f'''<div class="stats">
    <div class="rv"><b>2002</b><span>{t('成立于上海', 'Founded in Shanghai')}</span></div>
    <div class="rv d1"><b>6000<sup>+</sup></b><span>{t('累计安装手术室系统', 'Operating rooms installed')}</span></div>
    <div class="rv d2"><b>80<sup>+</sup></b><span>{t('“中国百佳医院”', 'of China’s Top 100 hospitals')}</span></div>
    <div class="rv d3"><b>400<sup>+</sup></b><span>{t('外科专家用户', 'Surgeons using our systems')}</span></div>
    <div class="rv d3"><b>31</b><span>{t('覆盖省市', 'Provinces served')}</span></div>
  </div>'''

    contact_kv = f'''<dl class="kv"><div><dt>{t('地址', 'Address')}</dt><dd>{ADDR[L]}</dd></div>
      <div><dt>{t('电话', 'Phone')}</dt><dd><a href="tel:+862152353552">{t('021-52353552', '+86 21-52353552')}</a></dd></div>
      <div><dt>{t('传真', 'Fax')}</dt><dd>{t('021-52356619', '+86 21-52356619')}</dd></div>
      <div><dt>{t('邮箱', 'Email')}</dt><dd><a href="mailto:marketing@concordmed.cn">marketing@concordmed.cn</a></dd></div></dl>'''

    def offices(extra=''):
        return f'''<ul class="loc-list"{extra}>
      <li class="hq"><b>{t('上海', 'Shanghai')}</b><span class="mono">01 · {t('总部', 'HQ')}</span></li>
      <li><b>{t('北京', 'Beijing')}</b><span class="mono">02 · {t('办事机构', 'Office')}</span></li>
      <li><b>{t('广州', 'Guangzhou')}</b><span class="mono">03 · {t('办事机构', 'Office')}</span></li></ul>'''

    def write(fname, content):
        if zh:  # Chinese style: no full stop at the end of a text block (inner sentences keep theirs)
            content = re.sub(r'。(?=(?:\s*</[A-Za-z0-9]+>)+)', '', content)
        with open(os.path.join(OUT, fname), 'w', encoding='utf-8') as f: f.write(content)

    # ---------- home ----------
    def home(fname):
        rows, pimgs = '', ''
        for i, c in enumerate(CATS):
            n = c['name']; ps = BY_CAT[n]
            rows += f'''<li data-name="{e(cname(n))}"><a class="line-row" href="{cat_href(n)}">
  <span class="no">{i+1:02d}</span><span class="nm">{e(cname(n))}</span>
  <span class="meta"><span><em>{t('产品', 'Items')}</em>{len(ps):02d}</span><span><em>{t('品牌', 'Brand')}</em>{e(cbrand(n))}</span></span>
  <span class="ar">{ARROW}</span><span class="ds">{e(cdesc(n))}</span></a></li>'''
            cover = ' class="cover"' if ps[0]['thumb'] == HERO_IMG else ''
            pimgs += f'<img src="{e(img(ps[0]["thumb"]))}" alt=""{cover}>'
        brands = ''.join(f'<a href="{cat_href(c["name"])}" title="{e(cbrand(c["name"]))}"><img src="{e(img(c["logo"]))}" alt="{e(cbrand(c["name"]))}" loading="lazy"></a>'
                         for c in CATS if c['logo'])
        brands += f'<a class="all" href="products.html">{t("全部产品", "All products")}{ARROW}</a>'
        body = f'''
<section class="hero">
  <div class="bg"><img src="{img(HERO_IMG)}" alt="{t('数字一体化智慧手术室', 'Digital integrated operating room')}"></div>
  <div class="wrap hero-body">
    <h1 class="display">{t('<span class="ln"><span>卓越，</span></span><span class="ln"><span>源自专业。</span></span>',
                           '<span class="ln"><span>Excellence,</span></span><span class="ln"><span>born of expertise.</span></span>')}</h1>
    <p class="lead">{t('上海康迎医疗器械有限公司自 2002 年起专注于医院数字化智慧手术室系统与设备，为医院提供数字一体化智慧手术室及远程手术云技术平台的整体解决方案。',
                       'Since 2002, Concord Medical has focused on digital, intelligent operating room systems — delivering complete integrated ORs and remote-surgery cloud platforms for hospitals across China.')}</p>
    <div class="actions"><a class="btn btn-light" href="contact.html">{t('联系我们', 'Contact us')} {ARROW}</a><a class="link" href="#products">{t('浏览产品线', 'Explore products')} {DOWN}</a></div>
  </div>
  <div class="hero-bar mono"><div class="wrap"><span class="left">{t('Digital Integrated Operating Room · 数字化智慧手术室', 'Digital Integrated Operating Room · Since 2002')}</span><span class="scroll">{t('向下滚动', 'Scroll')} <i></i></span></div></div>
</section>

<section class="sec" id="about"><div class="wrap">
  {eyebrow('01', t('关于康迎', 'About Concord'))}
  <div class="split">
    <h2 class="h2 rv">{t('智慧手术室，<br><span class="muted">让手术更从容。</span>', 'A smarter OR.<br><span class="muted">A calmer surgery.</span>')}</h2>
    <div class="copy rv d1">
      <p>{t('手术室不只是设备的集合。我们把照明、吊塔、影像与示教整合为一个系统，让外科团队专注于手术本身。',
            'An operating room is more than a collection of equipment. We bring lighting, pendants, imaging and teaching together as one system, so surgical teams can focus on the operation itself.')}</p>
      <p>{t('二十余年来，康迎与全国各地医院及医疗机构建立了长期合作，拥有覆盖全国的分销网络，以及一支经验丰富的市场技术支持与售后服务团队。',
            'For more than twenty years we have partnered with hospitals across China, backed by a national distribution network and an experienced technical support and service team.')}</p>
      <a class="link" href="about.html">{t('了解康迎', 'About Concord')} {ARROW}</a>
    </div>
  </div>
  <figure class="figure rv"><div class="frame"><img src="{img(HERO_IMG)}" alt="" loading="lazy"></div>
    <figcaption class="mono">{t('Fig. 01 — 数字一体化智慧手术室', 'Fig. 01 — Digital integrated operating room')}</figcaption></figure>
  <div class="facts">
    <div class="rv"><span class="mono">{t('系统', 'Systems')}</span><p>{t('智慧手术室整体方案、手术无影灯、医用吊塔与手术头灯', 'Integrated OR solutions, surgical lights, pendants and headlights')}</p></div>
    <div class="rv d1"><span class="mono">{t('网络', 'Network')}</span><p>{t('北京、上海、广州等主要地区设有办事机构', 'Offices in Beijing, Shanghai, Guangzhou and other key regions')}</p></div>
    <div class="rv d2"><span class="mono">{t('服务', 'Service')}</span><p>{t('专业市场技术支持与售后服务团队，全程跟进', 'Dedicated technical support and after-sales service, end to end')}</p></div>
  </div>
  {stats()}
</div></section>

<section class="sec white" id="products"><div class="wrap">
  <div class="sec-head"><div>{eyebrow('02', t('产品中心', 'Products'))}<h2 class="h2 rv">{t('七条产品线，<br><span class="muted">覆盖手术室核心场景。</span>', 'Seven product lines<br><span class="muted">for the modern OR.</span>')}</h2></div>
  <a class="link rv" href="products.html">{t('全部产品', 'All products')} {ARROW}</a></div>
  <div class="lines">
    <ul class="line-list">{rows}</ul>
    <aside class="preview" aria-hidden="true"><div class="pane">{pimgs}</div>
      <div class="cap mono"><b data-cap></b><span data-idx></span></div></aside>
  </div>
</div></section>

<section class="sec dark on-dark"><div class="wrap">
  <div class="sec-head"><div>{eyebrow('03', t('核心设备', 'Core equipment'))}<h2 class="h2 rv">{t('精密设备，<br><span class="muted">专业服务。</span>', 'Precision equipment.<br><span class="muted">Expert service.</span>')}</h2></div>
  <span class="mono rv" style="color:rgba(255,255,255,.45)">03 / 03</span></div>
  <div class="panels">
    <article class="panel rv">
      <div class="pic"><img src="{img('upfiles/20180913062328286.jpg')}" alt="{t('AMI LED 手术无影灯', 'AMI LED surgical light')}" loading="lazy"><span class="tag mono">01 / 03 <i></i></span></div>
      <div><span class="mono k">{t('01 — 照明与吊塔', '01 — Lights & pendants')}</span><h3 class="h3">{t('为术野而设计的光与空间。', 'Light and space, designed around the surgical field.')}</h3>
        <p>{t('LED 手术无影灯与多功能医用吊塔，采用高强度合金材质，表面易于清洁，符合高洁净手术室环境要求。',
              'LED surgical lights and multi-function pendants in high-strength alloy, with easy-clean surfaces suited to clean operating rooms.')}</p>
        <div class="specs"><div><span>{t('吊塔活动半径', 'Pendant reach')}</span><span>{t('最大 2500 mm', 'Up to 2,500 mm')}</span></div><div><span>{t('悬臂关节活动度', 'Arm rotation')}</span><span>340°</span></div><div><span>{t('无影灯', 'Surgical lights')}</span><span>AMI · SYSTEM TWO LED</span></div></div></div>
    </article>
    <article class="panel rv">
      <div class="pic"><img src="{img('upfiles/20141226075717755.png')}" alt="{t('奥美普外牵开器', 'OMNI-TRACT general surgery retractor')}" loading="lazy"><span class="tag mono">02 / 03 <i></i></span></div>
      <div><span class="mono k">{t('02 — 专科牵开器', '02 — Specialty retractors')}</span><h3 class="h3">{t('稳定暴露，<br>解放主刀的双手。', 'Steady exposure.<br>Free hands for the surgeon.')}</h3>
        <p>{t('OMNI-TRACT 奥美牵开器采用叉形臂框架系统，框架大小可调，贴近病人身体；拉钩可旋转变换角度，部件少、安装方便。',
              'OMNI-TRACT retractors use an adjustable fork-arm frame that sits close to the patient. Rotating blades change angle on demand, with few parts and quick set-up.')}</p>
        <div class="specs"><div><span>{t('框架系统', 'Frame')}</span><span>{t('叉形臂 · 可调', 'Fork-arm · adjustable')}</span></div><div><span>{t('专科覆盖', 'Specialties')}</span><span>{t('腔镜 · 骨科 · 泌尿 · 小儿 · 血管 · 移植', 'Lap · Ortho · Uro · Paeds · Vascular · Transplant')}</span></div><div><span>{t('脊柱拉钩', 'Spine blades')}</span><span>{t('可透 X 光', 'Radiolucent')}</span></div></div></div>
    </article>
    <article class="panel rv">
      <div class="pic"><img src="{img('upfiles/20150119074702540.png')}" alt="{t('暖宝快速输液恒温仪', 'Nuanbao IV fluid warmer')}" loading="lazy"><span class="tag mono">03 / 03 <i></i></span></div>
      <div><span class="mono k">{t('03 — 输液加温', '03 — Fluid warming')}</span><h3 class="h3">{t('即时加温，<br>精确到每一袋。', 'Instant warming,<br>precise for every bag.')}</h3>
        <p>{t('暖宝快速输液恒温仪支持 0.5L 至 3L 输液袋，双温控传感器精确控温，无需耗材，移动式、桌面式、壁挂式安装任选。',
              'The Nuanbao warmer takes 0.5 L to 3 L bags, uses dual sensors for precise control and needs no consumables — mobile, desktop or wall-mounted.')}</p>
        <div class="specs"><div><span>{t('加温至 40℃', 'To 40 °C')}</span><span>{t('少于 30 分钟', 'Under 30 min')}</span></div><div><span>{t('温差', 'Tolerance')}</span><span>+0 / −2 °C</span></div><div><span>{t('配置', 'Capacity')}</span><span>{t('1–6 袋 · 模块化', '1–6 bags · modular')}</span></div></div></div>
    </article>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><div>{eyebrow('04', t('服务流程', 'How we work'))}<h2 class="h2 rv">{t('从方案到交付，<br><span class="muted">全程专业陪伴。</span>', 'From plan to handover,<br><span class="muted">with you all the way.</span>')}</h2></div></div>
  <div class="steps">
    <div class="step rv"><span class="mono">Step 01</span><h3>{t('需求沟通', 'Consultation')}</h3><p>{t('了解科室与手术类型，梳理设备与系统需求。', 'We learn your departments and procedures and map out equipment needs.')}</p></div>
    <div class="step rv d1"><span class="mono">Step 02</span><h3>{t('方案设计', 'Solution design')}</h3><p>{t('基于数字一体化手术室平台，给出照明、吊塔与影像整合方案。', 'A plan that integrates lighting, pendants and imaging on one digital OR platform.')}</p></div>
    <div class="step rv d2"><span class="mono">Step 03</span><h3>{t('安装调试', 'Installation')}</h3><p>{t('由当地办事机构的技术人员完成安装、调试与使用培训。', 'Local engineers install, commission and train your team.')}</p></div>
    <div class="step rv d3"><span class="mono">Step 04</span><h3>{t('售后服务', 'Ongoing support')}</h3><p>{t('专业售后团队持续跟进，提供周到、及时的服务。', 'A dedicated service team keeps everything running.')}</p></div>
  </div>
</div></section>

<section class="sec white tight"><div class="wrap">
  <div class="sec-head"><div>{eyebrow('05', t('合作品牌', 'Brands'))}<h2 class="h2 rv">{t('值得信赖的<br><span class="muted">全球品牌。</span>', 'Trusted brands<br><span class="muted">from around the world.</span>')}</h2></div></div>
  <div class="brands rv">{brands}</div>
</div></section>

<section class="sec surf"><div class="wrap">
  <div class="sec-head"><div>{eyebrow('06', t('服务网络', 'Service network'))}<h2 class="h2 rv">{t('专业服务，<br><span class="muted">离您更近。</span>', 'Expert service,<br><span class="muted">close to you.</span>')}</h2></div></div>
  <div class="locs">
    <div class="rv">{offices()}</div>
    <div class="card rv d1"><span class="mono k">{t('总部 · 上海', 'Headquarters · Shanghai')}</span>
      {contact_kv}
      <div class="acts"><a class="btn btn-ink" href="contact.html">{t('在线留言', 'Send a message')} {ARROW}</a><a class="link" href="mailto:marketing@concordmed.cn">{t('发送邮件', 'Email us')} {ARROW}</a></div>
    </div>
  </div>
</div></section>'''
        return page(fname, t('康迎医疗 — 数字化智慧手术室', 'Concord Medical — Digital Integrated Operating Rooms'), 'home', body, over=True)

    # ---------- about ----------
    def about(fname):
        prose = ''.join(f'<p>{e(p)}</p>' for p in ABOUT[L])
        body = phead([('index.html', t('首页', 'Home')), (None, t('关于康迎', 'About'))], '01', t('关于康迎 · About', 'About Concord'),
                     t('卓越，<br><span class="muted">源自专业。</span>', 'Excellence,<br><span class="muted">born of expertise.</span>'),
                     t('自 2002 年起，专注医院数字化智慧手术室系统与设备。', 'Focused on digital, intelligent operating room systems and equipment since 2002.')) + f'''
<section class="sec" style="padding-top:0"><div class="wrap">
  <figure class="figure rv" style="margin-top:0"><div class="frame"><img src="{img(HERO_IMG)}" alt=""></div>
  <figcaption class="mono">{t('Fig. 01 — 数字一体化智慧手术室', 'Fig. 01 — Digital integrated operating room')}</figcaption></figure>
</div></section>
<section class="sec white"><div class="wrap split">
  <div class="stick">{eyebrow('02', t('公司简介', 'Company profile'))}<h2 class="h2 rv">{t('二十余年，<br><span class="muted">专注手术室。</span>', 'Twenty years<br><span class="muted">in the OR.</span>')}</h2></div>
  <div class="prose rv d1">{prose}</div>
</div>
<div class="wrap">{stats()}</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head"><div>{eyebrow('03', t('理念与文化', 'Values'))}<h2 class="h2 rv">{t('我们相信的事。', 'What we believe.')}</h2></div></div>
  <div class="values">
    <div class="value rv"><span class="mono">{t('经营理念', 'Business philosophy')}</span><blockquote>{t('卓越，源自专业。', 'Excellence, born of expertise.')}</blockquote><p>{t('以高品质的产品和完善的售后服务，赢得用户的信赖与支持。', 'Earning trust through high-quality products and complete after-sales service.')}</p></div>
    <div class="value light rv d1"><span class="mono">{t('企业文化', 'Culture')}</span><blockquote>{t('追求卓越，<br>止于至善。', 'Pursue excellence;<br>settle for nothing less.')}</blockquote><p>{t('为中国用户提供更高品质的产品和更加全面及时的服务。', 'Better products and more complete, timely service for our customers in China.')}</p></div>
  </div>
</div></section>''' + cta_band()
        return page(fname, t('关于康迎 — 康迎医疗', 'About — Concord Medical'), 'about', body)

    # ---------- catalog ----------
    def catalog():
        chips = f'<button class="chip on" data-cat="" aria-pressed="true">{t("全部", "All")} <small>{len(PRODUCTS):02d}</small></button>'
        for c in CATS:
            chips += f'<button class="chip" data-cat="{e(c["name"])}" aria-pressed="false">{e(cname(c["name"]))} <small>{len(BY_CAT[c["name"]]):02d}</small></button>'
        cards = ''.join(pcard(p, i) for i, p in enumerate(PRODUCTS))
        return f'''<div class="toolbar"><div class="chips" role="group" aria-label="{t('按产品线筛选', 'Filter by product line')}">{chips}</div>
  <label class="search">{SEARCH}<input type="search" placeholder="{t('搜索产品名称或型号', 'Search by product or model')}" aria-label="{t('搜索产品', 'Search products')}"></label></div>
  <p class="count mono" data-count></p>
  <div class="grid" data-filter>{cards}</div>
  <p class="empty" hidden>{t('没有找到匹配的产品，换个关键词试试。', 'No matching products — try another keyword.')}</p>'''

    def caseindex(fname):
        body = phead([('index.html', t('首页', 'Home')), (None, t('产品中心', 'Products'))], '02', t('产品中心 · Products', 'Products'),
                     t('产品中心', 'Products'),
                     t('七条产品线，覆盖智慧手术室、照明与吊塔、手术头灯、专科牵开器与输液加温。',
                       'Seven product lines: integrated ORs, lights and pendants, headlights, specialty retractors and fluid warming.')) + f'''
<section class="sec white" style="padding-top:56px"><div class="wrap">{catalog()}</div></section>''' + cta_band()
        return page(fname, t('产品中心 — 康迎医疗', 'Products — Concord Medical'), 'products', body)

    def case_page(c):
        n = c['name']; idx = ORDER.index(n) + 1
        chips = f'<a class="chip" href="products.html">{t("全部", "All")} <small>{len(PRODUCTS):02d}</small></a>' + ''.join(
            f'<a class="chip" href="{cat_href(x["name"])}"{CUR if x is c else ""}>{e(cname(x["name"]))} <small>{len(BY_CAT[x["name"]]):02d}</small></a>' for x in CATS)
        ps = BY_CAT[n]
        cards = ''.join(pcard(p, i) for i, p in enumerate(ps))
        body = phead([('index.html', t('首页', 'Home')), ('products.html', t('产品中心', 'Products')), (None, cname(n))], f'{idx:02d}',
                     t('产品线 · ', 'Product line · ') + cbrand(n), e(cname(n)), e(cdesc(n))) + f'''
<section class="sec white" style="padding-top:56px"><div class="wrap">
  <div class="toolbar"><nav class="chips" aria-label="{t('产品线', 'Product lines')}">{chips}</nav></div>
  <p class="count mono">{nprod(len(ps))}</p>
  <div class="grid">{cards}</div>
</div></section>''' + cta_band()
        return page(cat_file(n), f'{cname(n)} — {t("产品中心 — 康迎医疗", "Products — Concord Medical")}', 'products', body, desc=cdesc(n))

    # ---------- product detail ----------
    def product(p):
        ps = BY_CAT[p['cat']]; i = ps.index(p); fi = PRODUCTS.index(p)
        prev_p, next_p = PRODUCTS[fi - 1], PRODUCTS[(fi + 1) % len(PRODUCTS)]
        title = tr(p['title'])
        thumbs = ''
        if len(p['imgs']) > 1:
            thumbs = '<div class="thumbs">' + ''.join(
                f'<button data-src="{e(img(s))}" aria-pressed="{"true" if j==0 else "false"}" aria-label="{t("图片", "Image")} {j+1}"><img src="{e(img(s))}" alt=""></button>'
                for j, s in enumerate(p['imgs'])) + '</div>'
        if p['feats']:
            feats = '<ul class="feats">' + ''.join(
                f'<li class="sub">{e(tr(x))}</li>' if k == 'sub' else f'<li>{e(tr(x))}</li>' for k, x in p['feats']) + '</ul>'
        else:
            feats = f'<p class="note">{e(cdesc(p["cat"]))}<br>{t("详细技术参数与配置方案，欢迎联系我们获取。", "Contact us for full specifications and configuration options.")}</p>'
        model = (f'<div class="model"><span>{t("型号", "Model")}</span><span>{e(tr(p["model"]))}</span></div>' if p['model'] else
                 f'<div class="model"><span>{t("产品线", "Product line")}</span><span>{e(cname(p["cat"]))}</span></div>')
        related = [x for x in ps if x is not p][:3] or [x for x in PRODUCTS if x is not p][:3]
        rel = ''.join(pcard(x, j) for j, x in enumerate(related))
        body = f'''<section class="phead" style="padding-bottom:40px"><div class="wrap">
  <nav class="crumbs mono" aria-label="{t('面包屑', 'Breadcrumb')}"><a href="index.html">{t('首页', 'Home')}</a><i>/</i><a href="products.html">{t('产品中心', 'Products')}</a><i>/</i><a href="{cat_href(p['cat'])}">{e(cname(p['cat']))}</a><i>/</i><span>{e(title)}</span></nav>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="detail">
    <div class="gallery rv"><div class="main"><img src="{e(img(p['imgs'][0]))}" alt="{e(title)}"></div>{thumbs}</div>
    <div class="info rv d1">
      <span class="mono k">{i+1:02d} / {len(ps):02d} — {e(cname(p['cat']))}</span>
      <h1 class="h2">{e(title)}</h1>
      {model}
      {feats}
      <div class="acts"><a class="btn btn-ink" href="contact.html">{t('咨询此产品', 'Enquire about this product')} {ARROW}</a><a class="btn btn-line" href="{cat_href(p['cat'])}">{t('返回 ', 'Back to ')}{e(cname(p['cat']))}</a></div>
    </div>
  </div>
  <nav class="pn" aria-label="{t('上一个 / 下一个产品', 'Previous / next product')}">
    <a href="{prod_href(prev_p['id'])}"><span class="mono">← {t('上一个', 'Previous')}</span><b>{e(tr(prev_p['title']))}</b></a>
    <a href="{prod_href(next_p['id'])}"><span class="mono">{t('下一个', 'Next')} →</span><b>{e(tr(next_p['title']))}</b></a>
  </nav>
</div></section>
<section class="sec white tight"><div class="wrap">
  <div class="sec-head"><div>{eyebrow('—', t('相关产品', 'Related'))}<h2 class="h2 rv">{t('同系列产品', 'More in this line')}</h2></div><a class="link rv" href="{cat_href(p['cat'])}">{t('查看全部', 'View all')} {ARROW}</a></div>
  <div class="grid">{rel}</div>
</div></section>'''
        return page(prod_file(p['id']), f'{title} — {t("康迎医疗", "Concord Medical")}', 'products', body, desc=psum(p) or cdesc(p['cat']))

    # ---------- news ----------
    def news(fname):
        body = phead([('index.html', t('首页', 'Home')), (None, t('新闻中心', 'News'))], '04', t('新闻中心 · News', 'News'),
                     t('新闻中心', 'News'), t('公司动态、行业资讯与产品更新。', 'Company news, industry updates and product announcements.')) + f'''
<section class="sec white" style="padding-top:56px"><div class="wrap">
  <div class="toolbar"><div class="chips"><span class="chip on">{t('全部', 'All')}</span></div><span class="mono" style="color:var(--mute)">{t('00 篇', '00 posts')}</span></div>
  <div class="empty rv" style="padding:96px 0"><p class="mono" style="color:var(--teal)">{t('暂无新闻', 'No news yet')}</p>
  <h2 class="h3" style="margin:12px 0">{t('最新动态整理中。', 'Updates are on the way.')}</h2><p style="margin:0">{t('如需了解产品与项目信息，欢迎直接与我们联系。', 'For product or project information, please get in touch.')}</p>
  <p style="margin-top:28px"><a class="link" href="contact.html">{t('联系我们', 'Contact us')} {ARROW}</a></p></div>
</div></section>''' + cta_band()
        return page(fname, t('新闻中心 — 康迎医疗', 'News — Concord Medical'), 'news', body)

    # ---------- contact ----------
    def contact(fname):
        body = phead([('index.html', t('首页', 'Home')), (None, t('联系我们', 'Contact'))], '05', t('联系我们 · Contact', 'Contact'),
                     t('联系我们', 'Contact us'), t('产品咨询、方案设计或售后服务，欢迎随时与我们联系。', 'Product enquiries, solution design or service — we are here to help.')) + f'''
<section class="sec white" style="padding-top:56px"><div class="wrap locs">
  <div class="rv">{offices(' style="margin-bottom:40px"')}{contact_kv}</div>
  <div class="card rv d1"><span class="mono k">{t('在线留言', 'Send a message')}</span>
    <form class="form" action="http://concordmed.cn/contact.php?act=save" method="post" name="form1">
      <label><span class="mono">{t('您的称呼', 'Your name')}</span><input type="text" name="truename" autocomplete="name" required></label>
      <label><span class="mono">{t('联系电话', 'Phone')}</span><input type="tel" name="tel" autocomplete="tel"></label>
      <label class="full"><span class="mono">{t('邮箱地址', 'Email')}</span><input type="email" name="email" autocomplete="email" required></label>
      <label class="full"><span class="mono">{t('详细内容', 'Message')}</span><textarea name="message" placeholder="{t('请简要描述您的需求，例如科室、手术类型或感兴趣的产品', 'Tell us about your needs — department, procedures or products of interest')}" required></textarea></label>
      <div class="send"><small>{t('我们将在 1–2 个工作日内回复。', 'We reply within 1–2 business days.')}</small><button class="btn btn-ink" type="submit">{t('提交', 'Send')} {ARROW}</button></div>
    </form>
  </div>
</div></section>'''
        return page(fname, t('联系我们 — 康迎医疗', 'Contact — Concord Medical'), 'contact', body)

    # ---------- write ----------
    write('index.html', home('index.html'))
    write('about.html', about('about.html'))
    write('products.html', caseindex('products.html'))
    for c in CATS: write(cat_file(c['name']), case_page(c))
    for p in PRODUCTS: write(prod_file(p['id']), product(p))
    write('news.html', news('news.html'))
    write('contact.html', contact('contact.html'))
    return 5 + len(CATS) + len(PRODUCTS)


ADDR = {'zh': '上海市普陀区同普路 299 号<br>浙铁绿城长风中心 2 号楼 5 楼',
        'en': '5F, Building 2, Zhetie Greentown Changfeng Center<br>299 Tongpu Road, Putuo District, Shanghai, China'}
ABOUT = {
 'zh': [
  '上海康迎医疗器械有限公司成立于 2002 年，是一家致力于医院数字化智慧手术室系统和设备的专业化公司，为医院提供数字一体化智慧手术室系统及远程手术云技术平台的整体解决方案。',
  '随着中国医疗市场的蓬勃发展，康迎医疗抓住机遇，迎接挑战，秉承“卓越，源自专业”的经营理念，十多年来与全国各地医院及医疗机构建立了长期良好的合作关系。公司不仅建立了强大的全国性分销网络，而且拥有一支具有丰富专业知识、丰富经验的市场技术支持和售后服务团队，在北京、上海、广州等中国主要地区均建有办事机构，并都配有专业的市场技术和售后服务人员，为客户提供周到完善的服务，以高品质的产品和完善的售后服务赢得了广大用户的信赖和支持。',
  '康迎医疗在中国已累计完成安装了 6000 多间的手术室系统设备，涉及 80 多家“中国百佳医院”。迄今为止，中国已有 400 多位外科专家成为了我们的用户，遍及全国 31 个省市，深受专家的好评。',
  '上海康迎医疗器械有限公司贯彻“追求卓越，止于至善”的企业文化精神，将继续为中国的用户提供更高品质的产品和更加全面及时的服务，为创造一个美好和谐的医疗环境贡献一份力量。'],
 'en': [
  'Founded in 2002, Shanghai Concord Medical Equipment Co., Ltd. specialises in digital, intelligent operating room systems and equipment, providing hospitals with complete solutions for integrated digital operating rooms and remote-surgery cloud platforms.',
  'As China’s healthcare market has grown, Concord has embraced the opportunity under its philosophy of “Excellence, born of expertise”, building long-term partnerships with hospitals and medical institutions nationwide. Beyond a strong national distribution network, we have an experienced team of technical support and after-sales specialists, with offices in Beijing, Shanghai, Guangzhou and other key regions — earning customers’ trust through high-quality products and complete service.',
  'Concord has installed operating room systems in more than 6,000 operating rooms in China, including over 80 of the country’s Top 100 hospitals. More than 400 surgeons across 31 provinces now use our systems.',
  'Guided by our culture of “Pursue excellence; settle for nothing less”, we will keep bringing better products and more complete, timely service to our customers, and help create a better healthcare environment.'],
}

if __name__ == '__main__':
    print('zh pages:', build('zh'))
    print('en pages:', build('en'))
