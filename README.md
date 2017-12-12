# metonym
Domain specific language for generating analogous variations of textual inputs. The goal of this project is to more readily generate variations of text with entity annotations for use in systems such as Rasa NLU. 

### Grammar:
```
expression-list = expression | entity-expression, {expression | entity-expression};
entity-expression = expression entity;
expression = string | requirement | optional;
requirement = '[' option | {option} ']';
optional = '(' option | {option} ')';
option-list = option string;
option = string '|', {string '|'};
entity = ':' string;
string = term, {term};
term = char, {char};
char = letter, digit;
letter = "A" | "B" | "C" | "D" | "E" | "F" | "G"
       | "H" | "I" | "J" | "K" | "L" | "M" | "N"
       | "O" | "P" | "Q" | "R" | "S" | "T" | "U"
       | "V" | "W" | "X" | "Y" | "Z" | "a" | "b"
       | "c" | "d" | "e" | "f" | "g" | "h" | "i"
       | "j" | "k" | "l" | "m" | "n" | "o" | "p"
       | "q" | "r" | "s" | "t" | "u" | "v" | "w"
       | "x" | "y" | "z" | "-" | "_" ;
digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";
```

### Example
Consider the excerpt from the [Wikipedia article for the Roland JX-3P Synthesizer](https://en.wikipedia.org/wiki/Roland_JX-3P)...
> The Roland JX-3P is a synthesizer produced by Roland Corporation of Japan in 1983.

... and the various ways in which one could ask the question the question "Who made the JX-3P?"..

__Syntax Example__
```
[Who | [What | which] [company | brand]]:make [created|built|designed|produced] the [JX-3P:model] (synthesizer|keyboard|synth)?
```

Note: 
* An optional can not contain requirements, but a requirement can have options

__AST (Abstract Syntax Tree) Example__
```
Expression List:
  Entity-Expression: make
    Requirement:
      Option: 
        who
      Option:
        Requirement:
          Option: 
            what
          Option: 
            which
          Requirement:
            Option: company
            Option: brand
  Expression:
    Required:
      Option: created
      Option: built
      Option: designed
      Option: produced
  Expression:
    String: the
  Expression:
    Required:
      Entity: model
        string: JX-3P
  Expression:
    Optional:
      Option: synthesizer
      Option: keyboard
```

__Example Variations__ (clearly there are more variations)
```
Who created the JX3P?
What company created the JX3P?
What brand created the JX3P?
Who created the JX3P synthesizer?
Who created the JX3P keyboard?
Who created the JX3P synth?
Which brand created the JX3P synthesizer?
What company designed the JX3P keyboard?
...
```

__Rasa NLU Training Data Format__

Note that currently, the "intent" is not part of the syntax as it would be the same for each variation and can be added later when the training data is generated.
```
{
  "text": "Which brand created the JX3P synthesizer?",
  "intent": "synthesizer_make_query",
  "entities": [
    {
      "start": 0,
      "end": 11,
      "value": "Which brand",
      "entity": "make"
    }, {
       "start": 24, 
       "end": 41,
       "value": "JX3P synthesizer", 
       "entity": "make"
    }
  ]
}
```
