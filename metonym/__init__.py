import re
import string
import itertools

class Node:
  """
  A simple class containing a name and list of leaf nodes
  """
  def __init__(self, node_type):
    self.type = node_type
    self.value = ''
    self.nodes = []

  def __repr__(self):
    return str(vars(self))

  def __str__(self):
    s = self.__repr__().replace("'", '"')
    j = json.loads(s)
    return json.dumps(j, indent=1, sort_keys=True)

class Parser:
  """
  The base Parser class
  Provides a few utility methods and a method to override (expression) in sub-classes
  """
  def __init__(self):
    self.depth = 0
    self.index = 0
    self.logging = True
    self.logline = 0
    self.output = None
    self.tokens = []

  def go(self, input_string):
    """
    Invokes the creation of an abstract syntax tree through recursive decent parsing
    """
    self.depth = 0
    self.index = 0
    self.logline = 0
    self.tokens = re.findall(r"[\w\_\-']+|[\|\[\]\(\):]", input_string)
    self.output = Node('expression-list')
    tree = self.expression_list()
    if tree:
      self.output.nodes = tree
    return self.output

  def expression_list(self): 
    return self.one_or_more(self.expression)

  # primitive functions
  def execute(self, rule):
    bt = self.index
    self.depth += 1
    result = rule()
    self.depth -= 1 
    if result:
      return result
    self.log('back-tracking index from {} to {}'.format(self.index, bt))
    self.log('{} failed'.format(rule.__name__))
    self.index = bt

  def first_of(self, rules):
    """
    Return the result of the first rule that returns a valid result
    """
    for rule in rules:
      self.log('first_of -> {}'.format(rule.__name__))
      result = self.execute(rule)
      if result:
        return result

  def one_or_more(self, rule):
    """
    Return the valid result of one or more rules
    """
    nodes = []
    keep_going = True
    while keep_going:
      self.log('one_or_more -> {}'.format(rule.__name__))
      bt = self.index
      self.depth += 1
      result = rule()
      self.depth -= 1
      if result:
        nodes.append(result)
      else:
        self.index = bt
        keep_going = False

    if len(nodes):
      return nodes

  def require(self, rule):
    """
    Returns the result of a rule or throws if the result is None
    """
    self.log('require -> {}'.format(rule.__name__))
    node = rule()
    if not node:
      raise Error('The rule {} was required, but failed to output a valid result', rule.__name__)  
    return node

  def match(self, pattern):
    """
    Returns the result of a regex match at a specific index, None otherwise
    """
    if self.index < len(self.tokens):
      self.log('match -> {}'.format(pattern))
      m = re.match(pattern, self.tokens[self.index])
      if m:
        value = m.group(0)
        self.index += 1
        return value
    return None

  def next_char_is(self, c):
    """
    Return a boolean indicating whether or not the next character in the input matches the supplied parameter
    """
    if self.index < len(self.tokens):
      self.log('next_char_is {}'.format(c))
      if self.tokens[self.index] == c:
        self.index += 1
        return True
    return False

  def collapse(self, l):
    """
    Collapse a 2 dimensional list into a 1 dimensional list
    """
    return list(itertools.chain.from_iterable(l))

  def get_indent(self):
    indentation = '|'
    for i in range(0, self.depth-1):
      indentation += '-|'
    return indentation

  def log(self, msg): 
    if self.logging:
        logline_str = str(self.logline);
        if self.logline < 10:
          logline_str = "00" + logline_str
        if self.logline >= 10 and self.logline < 100:
          logline_str = "0" + logline_str
        self.logline += 1
        if self.index < len(self.tokens):
          print('{}. {} {}  {} - Token: {}'.format(logline_str, self.index, self.get_indent(), msg, self.tokens[self.index]))

class MetonymParser(Parser):
  def __init__(self):
    super(MetonymParser, self).__init__()

  def expression(self):
    lh_optionals = self.one_or_more(self.optional)
    result = self.first_of([
        self.option_list,
        self.requirement,
        self.string
      ])

    if result:
      entity = self.entity()
      rl_optionals = self.one_or_more(self.optional)
      node = Node('expression')
      node.nodes = self.collapse([
          lh_optionals or [],
          [result], 
          entity or [],
          rl_optionals or []
        ])
      return [node]

  def requirement(self):
    if self.next_char_is('['):
      result = self.first_of([
        self.option_list,
        self.string,
        self.requirement
      ])

      if result:
        if self.next_char_is(']'):
          node = Node('requirement')
          node.nodes = result
          return [node]

  def optional(self):
    if self.next_char_is('('):
      result = self.first_of([
          self.option_list,
          self.string
        ])

      if result:
        if self.next_char_is(')'):
          node = Node('optional')
          node.nodes = result
          return [node]

  def option_list(self):
    options = self.one_or_more(self.option) 
    if options:
      last_option = \
        self.one_or_more(self.string) or \
        self.one_or_more(self.requirement)

      if last_option:
        option = Node('option')
        option.nodes = [last_option]
        node = Node('option-list')
        node.nodes = self.collapse([options, [option]])
        return [node]

  def option(self):
    lhs = \
      self.one_or_more(self.string) or \
      self.one_or_more(self.requirement)

    if lhs:
      pipe = self.next_char_is('|')
      if pipe:
        node = Node('option')
        node.nodes = lhs
        return [node]

  def entity(self):
    colon = self.next_char_is(':')
    if colon:
      term = self.term()
      if term:
        node = Node('entity')
        node.value = term[0].value
        return [node]

  def string(self):
    result = self.one_or_more(self.term)
    if result:
      node = Node('string')
      node.nodes = result
      return [node]

  def term(self):
    m = self.match("[\w\-\_]+")
    if m:
      node = Node('term')
      node.value = m
      return [node]

if __name__ == '__main__':
  import json
  from json import tool
  p = MetonymParser()
  '''
  s = '[Who | [[What | which] [company | brand]]]:make'\
      '[created|built|designed|produced] the [JX-3P]:make'\
      '(synthesizer|keyboard|synth)?'
  '''
  #s = 'adios | goodbye | seeya [been nice getting to know you]'
  #s = '[123|[a b|c d]] [e f|c]] d e f (hello)'
  #s = '[who|[what|which] ]'
  s = '[Who | [What | Which] [company| maker]]:model [created|built|designed] the [JX3P]:make (synthesizer|keyboard|synth)'
  n = p.go(s)
  print(s)
  print(p.tokens)
  print(p.output)
