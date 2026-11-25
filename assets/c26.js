(function(){
  var d=document, root=d.documentElement;
  root.classList.remove('no-js');

  /* header: transparent over hero, frosted once scrolled */
  var hdr=d.querySelector('.hdr'), hero=d.querySelector('.hero');
  function onScroll(){
    if(!hdr) return;
    var y=window.scrollY||0;
    var over=hero && y < hero.offsetHeight-80;
    hdr.classList.toggle('is-over',!!over && y<40);
    hdr.classList.toggle('is-solid',!(over && y<40));
  }
  onScroll(); window.addEventListener('scroll',onScroll,{passive:true});

  var EN=root.lang.indexOf('en')===0;

  /* language switcher: remember an explicit choice */
  d.querySelectorAll('[data-setlang]').forEach(function(a){
    a.addEventListener('click',function(){ try{localStorage.setItem('c26-lang',a.getAttribute('data-setlang'))}catch(x){} });
  });
  var lang=d.querySelector('.lang'), lbtn=lang&&lang.querySelector('.lang-btn');
  if(lbtn){
    lbtn.addEventListener('click',function(ev){ev.stopPropagation(); var o=!lang.classList.contains('open'); lang.classList.toggle('open',o); lbtn.setAttribute('aria-expanded',o);});
    d.addEventListener('click',function(ev){ if(!lang.contains(ev.target)){lang.classList.remove('open'); lbtn.setAttribute('aria-expanded',false);} });
  }

  /* full-screen menu */
  var menu=d.querySelector('.menu');
  d.querySelectorAll('[data-menu]').forEach(function(b){
    b.addEventListener('click',function(){
      var open=!menu.classList.contains('open');
      menu.classList.toggle('open',open);
      d.body.style.overflow=open?'hidden':'';
      d.querySelectorAll('.burger').forEach(function(x){x.setAttribute('aria-expanded',open)});
    });
  });
  d.addEventListener('keydown',function(e){ if(e.key!=='Escape') return; if(menu&&menu.classList.contains('open')) d.querySelector('.menu .close').click(); if(lang&&lang.classList.contains('open')){lang.classList.remove('open'); lbtn.setAttribute('aria-expanded',false); lbtn.focus();} });

  /* reveal on scroll */
  var rv=d.querySelectorAll('.rv');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){ if(e.isIntersecting){e.target.classList.add('in'); io.unobserve(e.target);} })},{rootMargin:'0px 0px -8% 0px'});
    rv.forEach(function(el){io.observe(el)});
  } else rv.forEach(function(el){el.classList.add('in')});

  /* home: product-line list drives the sticky preview */
  var rows=d.querySelectorAll('.line-list li'), imgs=d.querySelectorAll('.preview .pane img'),
      capN=d.querySelector('.preview [data-cap]'), capI=d.querySelector('.preview [data-idx]');
  function pick(i){
    rows.forEach(function(r,j){r.classList.toggle('on',i===j)});
    imgs.forEach(function(m,j){m.classList.toggle('on',i===j)});
    if(capN) capN.textContent=rows[i].getAttribute('data-name');
    if(capI) capI.textContent=String(i+1).padStart(2,'0')+' / '+String(rows.length).padStart(2,'0');
  }
  rows.forEach(function(r,i){
    r.addEventListener('mouseenter',function(){pick(i)});
    r.addEventListener('focusin',function(){pick(i)});
  });
  if(rows.length) pick(0);

  /* catalog: chips + search */
  var cards=d.querySelectorAll('.grid[data-filter] .pcard');
  if(cards.length){
    var chips=d.querySelectorAll('.chips [data-cat]'), q=d.querySelector('.search input'),
        cnt=d.querySelector('[data-count]'), empty=d.querySelector('.empty'), cat='';
    function apply(){
      var s=(q&&q.value||'').trim().toLowerCase(), n=0;
      cards.forEach(function(c){
        var ok=(!cat||c.dataset.cat===cat)&&(!s||c.dataset.q.toLowerCase().indexOf(s)>-1);
        c.hidden=!ok; if(ok) n++;
      });
      if(cnt) cnt.textContent=EN?(n+(n===1?' product':' products')):(n+' 件产品');
      if(empty) empty.hidden=n>0;
    }
    chips.forEach(function(ch){
      ch.addEventListener('click',function(){
        cat=ch.dataset.cat; chips.forEach(function(x){x.classList.toggle('on',x===ch); x.setAttribute('aria-pressed',x===ch)});
        apply();
      });
    });
    if(q) q.addEventListener('input',apply);
    apply();
  }

  /* product gallery */
  var main=d.querySelector('.gallery .main img');
  d.querySelectorAll('.gallery .thumbs button').forEach(function(b,_,all){
    b.addEventListener('click',function(){
      main.src=b.dataset.src;
      all.forEach(function(x){x.setAttribute('aria-pressed',x===b)});
    });
  });
})();
