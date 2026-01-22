(function(){
  function getCookie(name){
    var v=document.cookie.match('(^|;)\s*'+name+'\s*=\s*([^;]+)');
    return v?v.pop():'';
  }
  var input=document.getElementById('search-input');
  var box=document.getElementById('search-suggestions');
  if(!input||!box){return;}
  var timer=null;
  var last='';
  function hide(){box.style.display='none';box.innerHTML='';}
  function show(items){
    if(!items.length){hide();return;}
    box.innerHTML='';
    items.forEach(function(it){
      var a=document.createElement('a');
      a.className='list-group-item list-group-item-action';
      a.href=it.url;
      a.textContent=it.title;
      box.appendChild(a);
    });
    box.style.display='block';
  }
  input.addEventListener('input',function(){
    var q=input.value.trim();
    if(q.length<2){hide();return;}
    if(q===last){return;}
    if(timer){clearTimeout(timer);}
    timer=setTimeout(function(){
      last=q;
      fetch('/ajax/search/?q='+encodeURIComponent(q),{credentials:'same-origin',headers:{'X-Requested-With':'XMLHttpRequest'}})
        .then(function(r){return r.json();})
        .then(function(data){show((data&&data.results)||[]);})
        .catch(function(){hide();});
    },300);
  });
  document.addEventListener('click',function(e){
    if(e.target===input||box.contains(e.target)){return;}
    hide();
  });
})();