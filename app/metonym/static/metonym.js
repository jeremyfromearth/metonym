function go() {
  // -------------------------------------------------------------
  //
  // Example Data
  //
  // -------------------------------------------------------------
  var examples = [
    {
      title: 'Asking for Directions', 
      syntax: '[Where can I find|How do I get to|Where is] [the|a|the nearset|a nearby] [market]:location?',
      intent: 'wayfinding'
    }, {
      title: 'Greetings', 
      syntax: '[Hello|Hi|Hey there|Hola|Hiya]:greeting',
      intent: 'greeting'
    }, {
      title: 'Multiple Entities',
      syntax: 'What [town|city|state|province|country]:location_type did you learn to [ride]:activity a [bike|skateboard|segway]:vehicle in?',
      intent: 'where-did-you-learn-question'
    }
  ];

  // -------------------------------------------------------------
  //
  // U.I.
  //
  // -------------------------------------------------------------
  var content = el('content');
  var intent_input = el('intent-input');
  var metonym_input = el('metonym-input');
  var error_bar = el('error-bar');
  var overview_txt = el('overview-text');
  var parse_btn = el('parse-btn');
  var raw_ast = el('raw-ast');
  var raw_rasa = el('raw-rasa');
  var example_select = el('example-select');
  var tree = TreeVisualization(content.clientWidth, content.clientHeight, '#svg')

  examples.forEach(function(item, idx) {
    var o = document.createElement("option", item);
    o.text = item.title;
    o.value = idx;;
    example_select.options.add(o, item);
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

  metonym_input.addEventListener('keyup', function() {
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
    var example = examples[example_select.value];
    metonym_input.value = example.syntax;
    intent_input.value = example.intent;
  }

  function parse_input() {
    tree.clear();
    raw_ast.value = '';
    raw_rasa.value = '';
    
    var xhr = new XMLHttpRequest();
    xhr.open('POST', './parse', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onload = function () {
      if(xhr.status == 200) {
        var result = JSON.parse(xhr.response);
        if(result.error) {
          error_bar.style.display = 'block';
          error_bar.innerHTML = result.error;
        } else {
          var ast = result.ast;
          if(ast) {
            tree.create(Object.assign({}, ast));
            raw_ast.value = JSON.stringify(JSON.parse(xhr.response).ast, null, 2);
          }

          var rasa = result.rasa;
          if(rasa) {
            raw_rasa.value = JSON.stringify(rasa, null, 2);
          }
        }
      } else {
        error_bar.style.display = 'block';
        error_bar.innerHTML = 'Server returned something other than a 200!';
      }
    };

    xhr.send(JSON.stringify({syntax: metonym_input.value, intent: intent_input.value}));
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
