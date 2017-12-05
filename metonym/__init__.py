import re
import string
import itertools

class Parser:
  def __init__(self):
    self.input = ''
    self.index = 0
    self.output = None

  def go(self, input_str):
    """
    Invokes the creation of an abstract syntax tree through recursive decent parsing
    """
    self.index = 0
    self.input = input_str
    self.output = self.expr() 
    return self.output

  def expr(self):
    # override w/ sub-class
    pass

  # primitive functions
  def first_of(self, rules):
    """
    Return the result of the first rule that returns a valid result
    """
    pass

  def one_or_more(self, rule):
    """
    Return the valid result of one or more rules
    """
    pass

  def required(self, rule):
    """
    Returns the result of a rule or throws if the result is None
    """
    pass

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

  def expr():
    node = None
    return node


if __name__ == '__main__':
  p = Parser()
  p.go(' hello world')
  p.char('')
  print(p.index)
