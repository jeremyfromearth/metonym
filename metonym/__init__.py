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
  def first_of(self, rules):
    """
    Return the result of the first rule that returns a valid result
    """
    for rule in rules:
      self.depth += 1
      bt = self.index
      self.log('first_of invoking {}'.format(rule.__name__))
      result = rule()
      self.depth -= 1
      if result:
        self.log('first_of {} is valid'.format(rule.__name__))
        return result
      else:
        self.depth -= 1
        self.index = bt
        pass

  def one_or_more(self, rule):
    """
    Return the valid result of one or more rules
    """
    nodes = []
    predicate = True
    while predicate and self.index < len(self.tokens):
      bt = self.index
      self.depth += 1
      self.log('one_or_more invoking {}'.format(rule.__name__))
      node = rule()
      self.depth -= 1
      if node is None:
        predicate = False
        self.index = bt
      else:
        self.log('one_or_more {} is valid'.format(rule.__name__))
        nodes.append(node)
    if len(nodes):
      return nodes

  def zero_or_more(self, rule):
    nodes = []
    keep_going = True
    while keep_going:
      self.depth += 1
      self.log('zero_or_more invoking {}'.format(rule.__name__))
      node = rule()
      self.depth -= 1
      if node:
        nodes.append(node)
        self.index += 1
      else:
        keep_going = False

    if len(nodes):
      return nodes

  def required(self, rule):
    """
    Returns the result of a rule or throws if the result is None
    """
    node = rule()
    if not node:
      raise Error('The rule {} was required, but failed to output a valid result', rule.__name__)  
    return node

  # utility functions
  def match(self, pattern):
    """
    Returns the result of a regex match at a specific index, None otherwise
    """
    if self.index < len(self.tokens):
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
      if self.tokens[self.index] == c:
        self.index += 1
        return True
    return False

  def collapse(self, l):
    """
    Collapse a 2 dimensional list into a 1 dimensional list
    """
    return list(itertools.chain.from_iterable(l))

  def  get_indent(self):
    indentation = ''
    for i in range(0, self.depth):
      indentation += '|-'
    return indentation

  def log(self, msg): 
    if self.logging:
        logline_str = str(self.logline);
        if self.logline < 10:
          logline_str = "00" + logline_str
        if self.logline >= 10 and self.logline < 100:
          logline_str = "0" + logline_str
        self.logline += 1
        print('{}. {} {} :: {}'.format(logline_str, self.index, self.get_indent(), msg))

class MetonymParser(Parser):
  def __init__(self):
    super(MetonymParser, self).__init__()

  def expression(self):
    self.log('expression')
    lh_optionals = self.zero_or_more(self.optional)
    result = self.first_of([
        self.requirement,
        self.string
      ])

    if result:
      entity = self.entity()
      rl_optionals = self.zero_or_more(self.optional)
      node = Node('expression')
      node.nodes = self.collapse([
          lh_optionals or [],
          [result], 
          entity or [],
          rl_optionals or []
        ])
      return [node]

  def requirement(self):
    self.log('requirement')
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
    self.log('optional')
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
    self.log('option_list')
    options = self.one_or_more(self.option) 
    if options:
      last_option = self.first_of([
          self.string,
          self.requirement
        ])

      if last_option:
        option = Node('option')
        option.nodes = [last_option]
        node = Node('option-list')
        node.nodes = self.collapse([options, [option]])
        return [node]

  def option(self):
    self.log('option')
    lhs = self.first_of([
        self.string,
        self.requirement,
      ])

    if lhs:
      pipe = self.next_char_is('|')
      if pipe:
        node = Node('option')
        node.nodes = lhs
        return [node]

  def entity(self):
    self.log('entity')
    colon = self.next_char_is(':')
    if colon:
      term = self.term()
      if term:
        node = Node('entity')
        node.value = term.value
        return [node]

  def string(self):
    self.log('string')
    result = self.one_or_more(self.term)
    if result:
      node = Node('string')
      node.nodes = result
      return [node]

  def term(self):
    self.log('term')
    m = self.match("[\w\-\_]+")
    if m:
      node = Node('term')
      node.value = m
      return [node]

if __name__ == '__main__':
  import json
  from json import tool
  p = MetonymParser()
  s = '[Who | [What | which] [company | brand]]:make'\
      '[created|built|designed|produced] the [JX-3P]:make'\
      '(synthesizer|keyboard|synth)?'
  n = p.go(s)
  print(p.index)
  print(p.tokens[p.index])
