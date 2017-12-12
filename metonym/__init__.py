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
    self.output = None
    self.tokens = []

  def go(self, input_string):
    """
    Invokes the creation of an abstract syntax tree through recursive decent parsing
    """
    self.depth = 0
    self.index = 0
    self.tokens = re.findall(r"[\w\_\-']+|[\|\[\]\(\):]", input_string)
    self.output = Node('expression-list')
    tree = self.one_or_more(self.expression)
    if tree:
      self.output.nodes = tree
    return self.output

  def expression(self): 
    # override in sub-classes
    return None

  # primitive functions
  def first_of(self, rules):
    """
    Return the result of the first rule that returns a valid result
    """
    for rule in rules:
      bt = self.index
      result = rule()
      if result:
        return result
      else:
        self.index = bt

  def one_or_more(self, rule):
    """
    Return the valid result of one or more rules
    """
    nodes = []
    predicate = True
    while predicate and self.index < len(self.tokens):
      bt = self.index
      self.depth += 1
      node = rule()
      self.depth -= 1
      if node is None:
        predicate = False
        self.index = bt
      else:
        nodes.append(node)
    if len(nodes):
      return nodes

  def zero_or_more(self, rule):
    nodes = []
    keep_going = True
    while keep_going:
      node = rule()
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

class MetonymParser(Parser):
  def __init__(self):
    super(MetonymParser, self).__init__()

  # expression = [optional] (requirement | string) [entity] [optional];
  def expression(self):
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

  # requirement = '[' option-list | string | requirement ']';
  def requirement(self):
    if self.next_char_is('['):
      result = self.first_of([
        self.option_list,
        self.string,
        self.requirement
      ])
      if result and self.next_char_is(']'):
        node = Node('requirement')
        node.children = result
        return node

  # optional = '(' option-list | string ')';
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
      string = self.string()
      if string:
        option = Node('option')
        option.nodes = [string]
        node = Node('option-list')
        node.nodes = self.collapse([options, [option]])
        return [node]

  def option(self):
    lhs = self.first_of([
        self.requirement,
        self.string
      ])
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
        node.value = term.value
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
  n = p.go('[hello i am a required string | i am something else] [synthesizer]')
  print(p.tokens)
  print(str(p.output))

