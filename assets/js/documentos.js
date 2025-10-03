// JS exemplo para módulo Documentos
(function(){
  let c = 0;
  function inc(){
    c++;
    const span = document.getElementById('ctr');
    if(span){ span.innerText = c; }
  }
  window.addEventListener('DOMContentLoaded', ()=>{
    const btn = document.getElementById('btnCount');
    if(btn){ btn.addEventListener('click', inc); }
  });
})();
