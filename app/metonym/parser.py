import re
import json
import itertools
from collections import Iterable

class Node:
  """
  A simple class containing a name and list of children
  """
  def __init__(self, node_type):
    self.name = node_type
    self.value = ''
    self.children = []

  def to_json(self):
    return json.dumps(self.__dict__, default=lambda o: o.__dict__)

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
      if result:
        self.log('first_of -> {}'.format(rule.__name__))
        self.depth -= 1
        return result
      self.depth -= 1
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

  def pre(self, in_str):
    """
    Metonym doesn't require any pre-processing, but this is a good chance to do some simple validation
    """
    # check for balanced parens
    lp = in_str.count('(')
    rp = in_str.count(')')
    if lp != rp:
      raise Exception('Parenthesis mis-match: {} left paren(s), {} right paren(s). '
        'Input must contain an equal number of both'.format(lp, rp))

    # check for balanced braces
    lb = in_str.count('[')
    rb = in_str.count(']')
    if lb != rb:
      raise Exception('Brace mis-match: {} left brace(s), {} right brace(s). '
        'Input must contain an equal number of both'.format(lb, rb))
      
    return in_str

  def lex(self, string):
    """
    Splits the string into words and terminal symbols
    """
    tokens = re.findall(r"[\w\_\-']+|[\|\[\]\(\):]", string)
    return tokens 

  def expression(self):
    result = self.first_of([
        self.requirement,
        self.option_list,
        self.optional,
        self.string
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
      result = self.one_or_more(self.requirement)

      if not result:
        result = self.first_of([
          self.option_list,
          self.string,
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
    self.idx = 0 

  def go(self, ast):
    def flatten(items, seqtypes=(list, tuple)):
      for i, x in enumerate(items):
        while i < len(items) and isinstance(items[i], seqtypes):
          items[i:i+1] = items[i]
      return items

    def permutate(tree, idx):
      if idx < len(tree):
        branch = tree[idx]
        for leaf in branch:
          for el in permutate(tree, idx+1):
            space = ' ' if leaf != '' else ''
            yield leaf + space + el
          if idx + 1 == len(tree):
            yield leaf
        
    def parse_node(node):
      if node.name == 'expression-list':
        parsed = []
        entities = {}
        for i in range(len(node.children)):
          child = node.children[i]
          for e in child.children:
            if e.name == 'entity':
              entities[i] = e
          parsed.append(parse_node(child))
        exprs = list(itertools.product(*parsed))
        
        results = []
        for i in range(len(exprs)):
          out = ''
          result = {'text':'', 'entities': []}
          for j in range(len(exprs[i])):
            start = len(out)
            out += exprs[i][j] + ' ' 
            end = len(out) - 2
            expr = exprs[i][j]
            if j in entities:
              if expr != '':
                result['entities'].append({
                  'value': exprs[i][j], 
                  'start': start, 
                  'end': end, 
                  'entity': entities[j].value
                })
            result['text'] = out.strip()
            results.append(result)
        return results
      elif node.name == 'requirement':
        parsed = [parse_node(n) for n in node.children]
        return list(permutate(parsed, 0))
      elif node.name == 'optional':
        return flatten([''] + [parse_node(n) for n in node.children])
      elif node.name == 'string':
        return [' '.join([term.value for term in node.children])]
      else:
        return flatten([parse_node(n) for n in node.children])
      return None
    return parse_node(ast)

class RasaCompiler(MetonymCompiler):
  def go(self, ast, intent_type):
    result = super(RasaCompiler, self).go(ast) 
    for r in result:
      r['intent'] = intent_type
    return json.dumps({
      'rasa_nlu_data': {
          'common_examples': result
        }
      })

if __name__ == '__main__':
  import json
  from json import tool
  parser = MetonymParser()

  #s = '[Where can I find|How do I get to|Where is] [the|a|the nearset|a nearby] market:location?'
  #s = '[Who | [[What | Which] [company | brand]]]:make [created|built|designed|produced] the [JX-3P]:model (synthesizer|keyboard|synth):instrument?'
  #s = '[I]:subject[am|am not|was|was not]:qualifier[a][human|machine|animal|plant]:object'
  #s = '[a|[[b][c|d]]]:test' # a, bc, bd
  #s = '[hello|goodbye|hey there|hola|seeya][world|earth|universe]'
  #s = '[Where can I find|How do I get to|Where is] [the|a|the nearset|a nearby] (grocery|shoe|instrument) store:location?'
  #s = 'What [town|city|state|province|country]:LOCATION_TYPE did you learn to ride a [bike|skateboard|segway]:VEHICLE in?'

  n = parser.go(s)
  if parser.index == len(parser.tokens):
    compiler = RasaCompiler()
    results = compiler.go(parser.output, 'test-intent')
    print(results)
  else:
    print('Parser Error at index {}'.format(parser.index))
