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
    return self.__str__()

  def __str__(self):
    return str(vars(self))

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
    self.tokens = re.findall(r"[\w\_\-']+|[\|\[\]\(\)]", input_string)
    self.output = Node('expression-list')
    tree = self.one_or_more(self.expression)
    if tree:
      self.output.nodes = self.collapse(tree) 
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
      node = rule()
      if node:
        return node
      else:
        self.index = bt

  def one_or_more(self, rule):
    """
    Return the valid result of one or more rules
    """
    nodes = []
    predicate = True
    while predicate and self.index < len(self.tokens):
      self.depth += 1
      node = rule()
      self.depth -= 1
      if node is None:
        predicate = False
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

  def look_at_char(self, expected, offset):
    """
    Returns a boolean indicating that the value of the token at the offset from the current index equals the expectation
    """
    idx = self.index + offset
    if idx < len(self.tokens):
      return self.tokens[idx] == expected
    return False

  def is_char(self, c):
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

  def expression(self):
    return self.string()

  def requirement(self):
    pass

  def option_list(self):
    bt = self.index
    pass

  def option(self):
    bt = self.index
    st = self.string()
    pipe = is_char('|')
    if st and pipe:
      node = Node('option')
      node.value = st
    pass

  def entity(self):
    colon = self.is_char(':')
    if colon:
      estr = self.string()
      if estr:
        node = Node('entity')
        node.value = estr.value
        return 

  def string(self):
    return self.one_or_more(self.term)

  def term(self):
    m = self.match("[\w\-\_]+")
    if m:
      result = Node('term')
      result.value = m
      return [result]

if __name__ == '__main__':
  p = MetonymParser()
  n = p.go('hello world')
  print(p.tokens)
  print(n)
