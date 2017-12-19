function go() {
  // -------------------------------------------------------------
  //
  // Example Data
  //
  // -------------------------------------------------------------
  var examples = {
    'Directions': '[Where can I find|How do I get to|Where is] [the|a|the nearset|a nearby] [market]:location?',
    'Greetings Option List': '[Hello|Hi|Hey there|Hola|Hiya]:greeting',
    'Multiple Entities': 'What [town|city|state|province|country]:location_type did you learn to ride a [bike|skateboard|segway]:vehicle in?'
  };

  // -------------------------------------------------------------
  //
  // U.I.
  //
  // -------------------------------------------------------------
  var content = el('content');
  var input = el('metonym-input');
  var error_bar = el('error-bar');
  var overview_txt = el('overview-text');
  var parse_btn = el('parse-btn');
  var raw_content = el('raw-result');
  var example_select = el('example-select');
  var tree = TreeVisualization(content.clientWidth, content.clientHeight, '#svg')

  Object.keys(examples).forEach(function(item) {
    var c = document.createElement("option", item);
    c.text = item;
    c.value = examples[item];
    example_select.options.add(c, item);
  });

  // -------------------------------------------------------------
  //
  // U.I. Update Methods
  //
  // -------------------------------------------------------------
  function show_tab(id) {
    var tabs = document.getElementsByClassName('content-tab');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].style.display = 'none'; 
    }
    var tab = el(id);
    if(tab) tab.style.display = 'flex'; 

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

  example_select.addEventListener('change', function(event) {
    update_input();
  });

  input.addEventListener('keyup', function() {
    error_bar.style.display = 'none';
  });

  // -------------------------------------------------------------
  //
  // Utils
  //
  // -------------------------------------------------------------
  function el(id) {
    return document.getElementById(id);
  }

  function update_input() {
    input.value = example_select.value
  }

  function parse_input() {
    tree.clear();
    raw_content.value = '';
    var xhr = new XMLHttpRequest();
    xhr.open('POST', './parse', true);
    xhr.setRequestHeader("Content-type", "text");
    xhr.onload = function () {
      if(xhr.status == 200) {
        var result = JSON.parse(xhr.response);
        if(result.error) {
          error_bar.style.display = 'block';
          error_bar.innerHTML = result.error;
        } else {
          show_tab('tree-view-tab');
          tree.create(Object.assign({}, result));
          raw_content.value = JSON.stringify(JSON.parse(xhr.response), null, 2);
        }
      } else {
        error_bar.style.display = 'block';
        error_bar.innerHTML = 'Server returned something other than a 200!';
      }
    };

    xhr.send(input.value);
  }

  // -------------------------------------------------------------
  //
  // Initialize
  //
  // -------------------------------------------------------------
  update_input();
  parse_input();
  show_tab('tree-view-tab');
}

window.addEventListener('load', go);
