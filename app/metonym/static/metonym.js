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
      title: 'Simple Greetings', 
      syntax: '[Hello|Hi|Hey there|Hola|Hiya]:greeting',
      intent: 'greeting'
    }, {
      title: 'Greeting With Follow Up',
      syntax: '[Hello|Hi|Hey there|Hola|Hiya]:greeting, (How\'s it going|How are you|What\'s up):follow_up?',
      intent: 'greeting'
    }, {
      title: 'Multiple Entities',
      syntax: 'What [town|city|state|province|country]:location_type did you learn to [ride]:activity a [bike|skateboard|segway]:vehicle in?',
      intent: 'where-did-you-learn-question'
    }, {
      title: 'Hotel Search', 
      syntax: '[I am|I\'m|We are|We\'re]:person ' + 
              '[searching|looking]:action for ' + 
              '[a place to stay|a hotel|an airbnb]:lodging_type '+
              'in [the city|Portland, Oregon|Columbus, Ohio|Berlin, Germany]:location ' + 
              '(May 1st|Saturday night|this weekend|tomorrow):date',
      'intent': 'hotel-search'
    }
  ];

  // -------------------------------------------------------------
  //
  // State
  //
  // -------------------------------------------------------------

  // The latest AST from the Metonym parser service
  var ast;

  // The latest Rasa results from the Metonym parser service
  var rasa;

  // A mapping of uuids to rasa objects
  var rasa_lookup;

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
  var summary = el('summary');
  var examples_container = el('examples-container');
  var example_select = el('example-select');
  var random_example_label = el('random-example-label');
  var random_example_slider = el('random-example-range');
  var select_all_checkbox = el('select-examples-checkbox');
  var select_all_label = el('select-examples-label');
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

  select_all_checkbox.addEventListener('change', function(event) {
    var checked = event.target.checked;
    select_all_label.innerHTML = checked ? 'Deselect All' : 'Select All';
    Object.keys(rasa_lookup).forEach(function(key) {
      var idx = rasa_lookup[key];
      var cb = el(`rasa-example-${idx}`).checked = checked;
    });
    random_example_slider.value = checked ? 1.0 : 0.0;
    random_example_label.innerHTML = `Random (Probability ${checked ? "1.00" : "0.00"})`;
  });

  random_example_slider.addEventListener('input', function(event) {
    var prob_str = event.target.value;;
    if(event.target.value == 1) {
      prob_str = "1.00";
      select_all_checkbox.checked = true;
      select_all_label.innerHTML = 'Deselect All';
    }

    if(event.target.value == 0) {
      prob_str = "0.00";
      select_all_checkbox.checked = false;
      select_all_label.innerHTML = 'Select All';
    }

    random_example_label.innerHTML = `Random (Probability ${event.target.value})`;
    Object.keys(rasa_lookup).forEach(function(key) {
      var idx = rasa_lookup[key];
      var checked = Math.random() < event.target.value;
      var cb = el(`rasa-example-${idx}`).checked = checked;
    });
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

  function clear(id) {
    var e = el(id);
    while(e.firstChild) e.removeChild(e.firstChild);
  }

  function update_input() {
    var example = examples[example_select.value];
    metonym_input.value = example.syntax;
    intent_input.value = example.intent;
  }

  function make_uuid() {
    var result = '';
    var symbols = 'abcdefghijklmnopqrstuvwxyz0123456789';
    for(var i = 0; i < 32; i++) {
      var index = Math.floor(Math.random() * symbols.length);
      var char = symbols[index];
      result += Math.random() > 0.5 ? symbols[index].toUpperCase() : symbols[index];
    }
    return result;
  }

  // -------------------------------------------------------------
  //
  // Service Calls
  //
  // -------------------------------------------------------------

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
          ast = result.ast;
          if(ast) {
            tree.create(Object.assign({}, ast));
            raw_ast.value = JSON.stringify(JSON.parse(xhr.response).ast, null, 2);
          }

          if(result.rasa) {
            rasa_lookup = {};
            rasa = result.rasa;
            raw_rasa.value = JSON.stringify(rasa, null, 2);
            var rasa_results = rasa.rasa_nlu_data.common_examples;
            var entity_data = {};
            select_all_checkbox.checked = true;
            select_all_label.innerHTML = 'Deselect All';
            random_example_slider.value = 1.0;
            random_example_label.innerHTML = `Random (Probability 1.00)`;
            rasa_results.forEach(function(item, idx) {
              item.entities.forEach(function(ent, idx) {
                if(entity_data[ent.entity]) {
                  entity_data[ent.entity].count += 1;
                } else {
                  entity_data[ent.entity] = {
                    color_class: 'entity-' + ((idx+1)%10),
                    count: 1
                  };
                }
              });
            });

            clear('summary');
            clear('examples-container');

            var entity_summary = 
              `<h3>Intent: ${intent_input.value}</h3> 
               <h3>Entities</h3>
               <ul class="entity-list">`;

            Object.keys(entity_data).forEach(function(item, idx) {
              var ent = entity_data[item]
              entity_summary += `<li class="entity-li ${ent.color_class}">${item}: ${ent.count}</li>`;
            });

            entity_summary += '</ul>'
            summary.innerHTML = `<h2>Number of Examples ${rasa_results.length}</h2> ${entity_summary}`;

            var rasa_examples_str = '';
            rasa_results.forEach(function(result, eidx) {
              var parts = [];
              var uuid = make_uuid();
              var entity_idx_map = {}
              var text = result.text;
              var entities = result.entities;
              
              rasa_lookup[uuid] = eidx;
              entities.forEach(function(entity) {
                entity_idx_map[entity.start] = entity;
              });

              // Wrap entities in colored labels
              var cidx = 0;
              rasa_examples_str += 
                `<div class="example-row">
                 <div class="example-id">${eidx+1}.</div>
                 <div class='example-wrapper'>
                 `
                
              while(cidx < text.length) {
                if(entity_idx_map[cidx]) {
                  var ent = entity_idx_map[cidx];
                  rasa_examples_str += `<div class="entity ${entity_data[ent.entity].color_class}"}">`;
                  while(cidx < ent.end+1) {
                    rasa_examples_str += text[cidx];
                    cidx++;
                  }
                  rasa_examples_str += '</div>';
                } else {
                  rasa_examples_str += text[cidx]
                  cidx++;
                }
              }

              rasa_examples_str += ` 
                <input id='rasa-example-${eidx}' 
                       type="checkbox" 
                       value="${uuid}" 
                       class="example-checkbox" 
                       checked="true">
                </input>
                </div></div>`;
            });
            
            examples_container.innerHTML = rasa_examples_str;
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
  show_tab('output-tab');
}

window.addEventListener('load', go);
