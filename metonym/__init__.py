import re

class Parser:
  def __init__(self):
    self.input = ''
    self.index = 0
    self.output = None

  def go(self):
    """
    Invokes the creation of an abstract syntax tree through recursive decent parsing
    """
    self.index = 0
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
  def match(self, regex, expected_match_input=0):
    """
    Returns the result of a regex match at a specific index, None otherwise
    """
    pass

  def char(self, c):
    """
    Return a boolean indicating whether or not the next character in the input matches the supplied parameter
    """
    pass

  def ignore_whitespace(self):
    """
    Advances index until a non whitespace character is reached
    """
    pass

class MetonymParser(Parser):
  def __init__(self):
    pass

  def expr():
    node = None
    return node

