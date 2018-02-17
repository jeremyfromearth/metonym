import re
import json
import string
import itertools
from collections import Iterable

class Node:
  """
  A simple class containing a name and list of leaf children
  """
  def __init__(self, node_type):
    self.name = node_type
    self.value = ''
    self.children = []

  def __repr__(self):
    return json.dumps(self.__dict__, default=lambda o: o.__dict__)

  def __str__(self):
    return self.__repr__()

class Parser:
  """
  The base Parser class
  Provides a few utility methods and methods to override (expression) in sub-classes
  """
  def __init__(self):
    self.depth = 0
    self.index = 0
    self.logging = False
    self.logline = 0
    self.output = None
    self.tokens = []

  def pre(self, string):
    """
    Return the preprocessed string or throw if string is not valid
    """
    raise Exception('The method pre() must be overridden by the Parser sub-class')

  def lex(self, string):
    """
    Return the tokenized string as a list of tokens
    """
    raise Exception('The method lex() must be overridden by Parser sub-class')

  def expression(self):
    """
    Define the basic composition of an expression
    """
    raise Exception('The method expression() must be overidden by Parser sub-class')

  def go(self, string):
    """
    Invoke the creation of an abstract syntax tree through recursive decent parsing
    """
    self.depth = 0
    self.index = 0
    self.logline = 0
    self.input = self.pre(string)
    self.tokens = self.lex(self.input)
    self.output = Node('expression-list')
    tree = self.expression_list()
    if tree:
      self.output.children = tree
    return self.output

  def expression_list(self): 
    """
    Returns an AST consiting of one or more expressions child children
    """
    return self.collapse(self.one_or_more(self.expression))

  def first_of(self, rules):
    """
    Return the result of the first rule that returns a valid result
    """
    for rule in rules:
      self.log('first_of -> {}'.format(rule.__name__))
      self.depth += 1
      bt = self.index
      result = rule()
      self.depth -= 1
      if result:
        return result
      self.index = bt

  def one_or_more(self, rule):
    """
    Return the valid result of one or more rules
    """
    children = []
    keep_going = True
    while keep_going:
      self.log('one_or_more -> {}'.format(rule.__name__))
      bt = self.index
      self.depth += 1
      result = rule()
      self.depth -= 1
      if result:
        children.append(result)
      else:
        self.index = bt
        keep_going = False

    if len(children):
      return children

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
    result = []
    for item in l:
      if type(item) == type([]):
        for x in item:
          result.append(x)
      else:
        result.append(item)
    return result

  def get_indent(self):
    """
    Computes the indentation level for the current logline
    """
    indentation = '|'
    for i in range(0, self.depth-1):
      indentation += '-|'
    return indentation

  def log(self, msg): 
    """
    Formats a string for logging and appends the supplied msg param
    """
    if self.logging:
      # TODO: Update this logging code to handle n log lines
      # this assumes that we'll have fewer than 1000 lines
      logline_str = str(self.logline);
      if self.logline < 10:
        logline_str = "00" + logline_str
      if self.logline >= 10 and self.logline < 100:
        logline_str = "0" + logline_str
      self.logline += 1
      if self.index < len(self.tokens):
        print('{}. {} {}  {} - Token: {}'
          .format(logline_str, self.index, self.get_indent(), msg, self.tokens[self.index]))

class MetonymParser(Parser):
  def __init__(self):
    super(MetonymParser, self).__init__()

  def pre(self, in_string):
    """
    Metonym doesn't require any pre-processing, but this is a good chance to do some simple validation
    """
    # check for balanced parens
    lp = in_string.count('(')
    rp = in_string.count(')')
    if lp != rp:
      raise Exception('Parenthesis mis-match: {} left paren(s), {} right paren(s). '
        'Input must contain an equal number of both'.format(lp, rp))

    # check for balanced braces
    lb = in_string.count('[')
    rb = in_string.count(']')
    if lb != rb:
      raise Exception('Brace mis-match: {} left brace(s), {} right brace(s). '
        'Input must contain an equal number of both'.format(lb, rb))
      
    return in_string

  def lex(self, string):
    """
    Splits the string into words and terminal symbols
    """
    tokens = re.findall(r"[\w\_\-']+|[\|\[\]\(\):]", string)
    return tokens 

  def expression(self):
    result = self.first_of([
        self.option_list,
        self.requirement,
        self.string,
        self.optional,
      ])

    if result:
      entity = self.entity()
      node = Node('expression')
      node.children = self.collapse([
          result, 
          entity or [],
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
          node.children = self.collapse(result)
          return [node]

  def optional(self):
    if self.next_char_is('('):
      result = self.first_of([
          self.expression,
          self.option_list,
          self.string
        ])

      if result:
        if self.next_char_is(')'):
          node = Node('optional')
          node.children = self.collapse(result)
          return [node]

  def option_list(self):
    options = self.one_or_more(self.option) 
    if options:
      last_option = \
        self.one_or_more(self.string) or \
        self.one_or_more(self.requirement)

      if last_option:
        last = Node('option')
        last.children = self.collapse(last_option)
        options.append(last)

        node = Node('option-list')
        node.children = self.collapse(options)
        return [node]

  def option(self):
    lhs = \
      self.one_or_more(self.string) or \
      self.one_or_more(self.requirement)

    if lhs:
      pipe = self.next_char_is('|')
      if pipe:
        node = Node('option')
        node.children = self.collapse(lhs)
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
      node.children = self.collapse(result)
      return [node]

  def term(self):
    m = self.match("[\w\-\_']+")
    if m:
      node = Node('term')
      node.value = m
      return [node]

class MetonymCompiler:
  def __init__(self):
    #self.root = root
    pass

  '''
  def parse_option_list(self, node):
    def _parse(node, idx):
      if idx < len(node):
        child = node.children[idx]
        for ch1 in child.children:
          for ch2 in _parse(node.children, idx+1):
            yield ch1 + ' ' + ch2
          if idx + 1 == len(node.children):
            yield ch1 
    for result in _parse(node, 0):
      yield result
  '''

  def go(self, ast): 
    print('--------------- go() ---------------')
    def _string(s):
      result = ''
      for term in s.children:
        result += term.value + ' '
      yield result

    def _option(option):
      for child in option.children:
        if child.name == 'string':
          for r in _string(child):
            yield r
        else:
          for r in _expr(child):
            yield r

    def _option_list(ol):
      for op in ol.children:
        for r in _option(op):
          yield r

    def _parse(expr, out=''):
      for child in expr.children:
        if child.name == 'expression':
          exp = []
          for r in _parse(child):
            exp.append(r)
          yield exp
        elif child.name == 'string':
          for r in _string(child):
            yield r
        elif child.name == 'option-list':
          for r in _option_list(child):
            yield r
        else:
          for r in _parse(child):
            yield r

    def _parse2(tree):
      def _parse(tree, idx):
        if idx < len(tree):
          branch = tree[idx]
          for leaf in branch:
            for el in _parse(tree, idx+1):
              yield leaf + ' ' + el
            if idx + 1 == len(tree):
              yield leaf
      for result in _parse(tree, 0):
        yield result

    expressions = [x for x in _parse(ast)] 
    result = [x for x in _parse2(expressions)]
    return result

    '''
    def _requirement(node, out=''):
      yield node.children

    def _expression(node, out=''):
      for child in node.children:
        yield out + child.name

    for child in ast.children:
      for x in _expression(child):
        yield x

    import random
    def a():
      for i in range(0, random.randint(1, 4)):
        yield 'a'

    def b():
      for i in range(0, random.randint(1, 4)):
        yield 'b'

    s = 'abba'
    for x in s:
      if x == 'a':
        for y in a():
          yield y
      if x == 'b':
        for y in b():
          yield y
    '''
    
if __name__ == '__main__':
  import json
  from json import tool
  parser = MetonymParser()
  s = 'What [town|city|state|province|country]:location_type did you learn to ride a [bike|skateboard|segway]:vehicle in?'
  n = parser.go(s)
  if parser.index == len(parser.tokens):
    compiler = MetonymCompiler()
    results = compiler.go(parser.output)
    for x in results:
      print(x)
  else:
    print('Parser Error at index {}'.format(parser.index))
  """
  results = [{
      text: 'Who created the JX3P?,
      entities: [{
          value: Who,
          start: 0, 
          end: 4,
          entity: make
        }, {
          value: JX3P,
          start: 16, 
          end: 19,
          entity: model
        }
      ]
    }]
  """
