import re
import string
import itertools

class ASTNode:
  """
  A simple class containing a name and list of leaf nodes
  """
  def __init__(self, name):
    self.name = name
    self.branches = []

class Parser:
  """
  The base Parser class. It provides a few utility methods and a method to override (expression) in sub-classes
  """
  def __init__(self):
    self.depth = 0
    self.input = ''
    self.index = 0
    self.output = None

  def go(self, input_str):
    """
    Invokes the creation of an abstract syntax tree through recursive decent parsing
    """
    self.depth = 0
    self.index = 0
    self.input = input_str
    self.output = ASTNode('expression-list')
    tree = self.one_or_more(self.expression)
    if tree is not None:
      self.output.branches = self.collapse(tree) 
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
      if result is not None:
        return result
      else:
        self.index = bt

  def one_or_more(self, rule):
    """
    Return the valid result of one or more rules
    """
    results = []
    predicate = True
    while predicate:
      bt = self.index  
      self.depth += 1
      result = rule()
      self.depth -= 1
      if result is None:
        self.index = bt
        predicate = False
      else:
        results.push(result)
    if len(results):
      return results
    else:
      self.index = bt

  def required(self, rule):
    """
    Returns the result of a rule or throws if the result is None
    """
    result = rule()
    if not result:
      raise Error('The rule {} was required, but failed to output a valid result', rule.__name__)  
    return result

  # utility functions
  def match(self, pattern):
    """
    Returns the result of a regex match at a specific index, None otherwise
    """
    if self.index < len(self.input):
      m = re.match(pattern, self.input)
      if m is not None:
        value = m.group(0)
        self.index += len(value)
        return value
    return None

  def char(self, c):
    """
    Return a boolean indicating whether or not the next character in the input matches the supplied parameter
    """
    if self.index < len(self.input):
      if self.input[self.index] == c:
        self.index += 1
        return True
    return False

  def ignore_whitespace(self):
    """
    Advances index until a non whitespace character is reached
    """
    while self.index < len(self.input):
      if self.input[self.index] in string.whitespace:
        self.index += 1
      else:
        break

  def collapse(self, l):
    """
    Collapse a 2 dimensional list into a 1 dimensional list
    """
    return list(itertools.chain.from_iterable(l))

class MetonymParser(Parser):
  def __init__(self):
    pass

  def expression():
    node = ASTNode('expression')
    return node

if __name__ == '__main__':
  p = Parser()
  node = p.go('What [(city | town | province | village | bourough] [(were you born in | did you grow up in)]')
  print(vars(node))
