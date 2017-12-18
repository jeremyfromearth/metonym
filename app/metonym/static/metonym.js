function el(id) {
  return document.getElementById(id);
}

function go() {
  var content = el('content');
  var input = el('metonym-input');
  var parse_btn = el('parse-btn');
  var tree = TreeVisualization(content.clientWidth, content.clientHeight, '#svg')

  input.value = '[Who | [What | which] [company | brand]]:make '+
    '[created|built|designed|produced] the [JX-3P]:model (synthesizer|keyboard|synth)'

  parse_btn.addEventListener('click', function() {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', './parse', true);
    xhr.setRequestHeader("Content-type", "text");
    xhr.onload = function () {
      if(xhr.status == 200) {
        var result = JSON.parse(xhr.response);
        tree.create(result);
      } else {
        console.log('error');
      }
    };

    var data = input.value;
    xhr.send(input.value);
  });

  window.addEventListener('resize', function(event) {
    if(tree) {
      tree.set_size(content.clientWidth, content.clientHeight)
    }
  });

  d3.selectAll('.menu-li')
    .on('mousedown', function(evt) {
      show_tab(this.dataset.tab);
      var selected = this;
      
    });

  function show_tab(id) {
    var tabs = document.getElementsByClassName('content-tab');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].style.display = "none"; 
    }
    var tab = el(id);
    if(tab) tab.style.display = "block"; 

    d3.selectAll('.menu-li').each(function(li) {
      if(this.dataset.tab == id) {
        this.style.color = 'rgb(66, 184, 221)'
      } else {
        this.style.color = '#ccc';
      }
    });
  }

  show_tab('overview-tab');
}

window.addEventListener('load', go);
