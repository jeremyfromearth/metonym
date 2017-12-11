# metonym
Domain specific language for generating analogous variations of textual inputs. The goal of this project is to more readily generate variations of text with entity annotations for use in systems such as Rasa NLU. 

### Grammar:
```
expression_list = expression, expression-list
expression = (string | optional | requirement), {string, optional | requirement};
entity = (string, requirement, optional) ':' string;
requirement = '[' (string | optional | requirement), {string | optional | requirement} ']';
optional = '(' (string | optional | requirement), {string | optional | requirement} ')';
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
Consider the excerpt from the Wikipedia article for Roland JX3P...
> The Roland JX-3P is a synthesizer produced by Roland Corporation of Japan in 1983.

... and the various ways in which one could ask the question the question "Who made the JX-3P?"..

__Syntax Example__
```
[(Who | [[What | which] [company | brand)]])]:make [created|built|designed|produced] the [JX-3P (synthesizer | keyboard | synth)]:model?
```

__AST (Abstract Syntax Tree) Example__
```
Expression:
    Entity: make
        Requirement:
            Optional:
                Option: who
                Option:
                    Requirement:
                        Requirement:
                            Optional:
                                Option: what
                                Option: which
                        Requirement:
                            Optional:
                                Option: company
                                Option: brand
    Required:
        Optional:
            Option: created
            Option: built
            Option: designed
            Option: produced
    String: the
    Entity: model
        Required:
            string: JX-3P
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
