var kl, pj;

kl = window.kl;

pj = kl.pj;

pj.init = function(kl_config, app_config, success, fail) {
  pj._make_div();
  kl.project_imported.trigger();
  success();
};

pj._make_div = function() {
  var div;
  div = document.createElement('div');
  div.id = 'human_ocr';
  if (document.body.firstChild) {
    document.body.insertBefore(div, document.body.firstChild);
  } else {
    document.body.appendChild(div);
  }
};

pj.on_task_received = function(data) {};
