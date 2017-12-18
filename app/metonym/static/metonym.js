function go() {
  // -------------------------------------------------------------
  //
  // Example Data
  //
  // -------------------------------------------------------------
  var examples = [{
      name: 'Greetings Option List',
      text: '[Hello|Hi|Hey there|Hola|Hiya]:greeting'
    }, {
      name: 'Multiple Entities',
      text: 'What [town|city|state|province|country]:location_type did you learn to ride a [bike|skateboard|segway]:vehicle in?'
    }
  ];

  // -------------------------------------------------------------
  //
  // U.I.
  //
  // -------------------------------------------------------------
  var content = el('content');
  var input = el('metonym-input');
  var parse_btn = el('parse-btn');
  var example_select = el('example-select');
  var tree = TreeVisualization(content.clientWidth, content.clientHeight, '#svg')

  // -------------------------------------------------------------
  //
  // U.I. Update Methods
  //
  // -------------------------------------------------------------
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

  // -------------------------------------------------------------
  //
  // U.I. Event Handlers
  //
  // -------------------------------------------------------------
  parse_btn.addEventListener('click', parse_input);

  window.addEventListener('resize', function(event) {
    if(tree) {
      tree.set_size(content.clientWidth, content.clientHeight)
    }
  });

  d3.selectAll('.menu-li')
    .on('mousedown', function(evt) {
      show_tab(this.dataset.tab);
    });

  // -------------------------------------------------------------
  //
  // Utils
  //
  // -------------------------------------------------------------
  function el(id) {
    return document.getElementById(id);
  }

  function parse_input() {
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
  }

  // -------------------------------------------------------------
  //
  // Initialize
  //
  // -------------------------------------------------------------
  show_tab('overview-tab');
}

window.addEventListener('load', go);
