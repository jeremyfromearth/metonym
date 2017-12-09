# metonym
Domain specific language for generating analogous variations of textual inputs. 

### Grammar:
__Rules__
```
expression = (string | optional | requirement), {string, optional | requirement};
entity = (string | requirement | optional) ':' string;
requirement = '[' string, entity, optional, requirement ']';
optional = '(' {option} ')';
option = [string '|', optional '|', requirement '|'];
string = term, {term};
term = char, {char | };
char = letter, digit;
letter = "A" | "B" | "C" | "D" | "E" | "F" | "G"
       | "H" | "I" | "J" | "K" | "L" | "M" | "N"
       | "O" | "P" | "Q" | "R" | "S" | "T" | "U"
       | "V" | "W" | "X" | "Y" | "Z" | "a" | "b"
       | "c" | "d" | "e" | "f" | "g" | "h" | "i"
       | "j" | "k" | "l" | "m" | "n" | "o" | "p"
       | "q" | "r" | "s" | "t" | "u" | "v" | "w"
       | "x" | "y" | "z" | "-" | "_" ;
digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
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

__Variations__
```
Who created the JX3P?
Who created the JX3P synthesizer?
Who created the JX3P keyboard?
Who created the JX3P synth?
What company created the JX3P?
What company created the JX3P synthesizer?
What company created the JX3P keyboard?
What company created the JX3P synth?
What brand created the JX3P?
What brand created the JX3P synthesizer?
What brand created the JX3P keyboard?
What brand created the JX3P synth?
Which company created the JX3P?
Which company created the JX3P synthesizer?
Which company created the JX3P keyboard?
Which company created the JX3P synth?
Which brand created the JX3P?
Which brand created the JX3P synthesizer?
Which brand created the JX3P keyboard?
Which brand created the JX3P synth?
Who built the JX3P?
Who built the JX3P synthesizer?
Who built the JX3P keyboard?
Who built the JX3P synth?
What company built the JX3P?
What company built the JX3P synthesizer?
What company built the JX3P keyboard?
What company built the JX3P synth?
What brand built the JX3P?
What brand built the JX3P synthesizer?
What brand built the JX3P keyboard?
What brand built the JX3P synth?
Which company built the JX3P?
Which company built the JX3P synthesizer?
Which company built the JX3P keyboard?
Which company built the JX3P synth?
Which brand built the JX3P?
Which brand built the JX3P synthesizer?
Which brand built the JX3P keyboard?
Which brand built the JX3P synth?
Who designed the JX3P?
Who designed the JX3P synthesizer?
Who designed the JX3P keyboard?
Who designed the JX3P synth?
What company designed the JX3P?
What company designed the JX3P synthesizer?
What company designed the JX3P keyboard?
What company designed the JX3P synth?
What brand designed the JX3P?
What brand designed the JX3P synthesizer?
What brand designed the JX3P keyboard?
What brand designed the JX3P synth?
Which company designed the JX3P?
Which company designed the JX3P synthesizer?
Which company designed the JX3P keyboard?
Which company designed the JX3P synth?
Which brand designed the JX3P?
Which brand designed the JX3P synthesizer?
Which brand designed the JX3P keyboard?
Which brand designed the JX3P synth?
Who produced the JX3P?
Who produced the JX3P synthesizer?
Who produced the JX3P keyboard?
Who produced the JX3P synth?
What company produced the JX3P?
What company produced the JX3P synthesizer?
What company produced the JX3P keyboard?
What company produced the JX3P synth?
What brand produced the JX3P?
What brand produced the JX3P synthesizer?
What brand produced the JX3P keyboard?
What brand produced the JX3P synth?
Which company produced the JX3P?
Which company produced the JX3P synthesizer?
Which company produced the JX3P keyboard?
Which company produced the JX3P synth?
Which brand produced the JX3P?
Which brand produced the JX3P synthesizer?
Which brand produced the JX3P keyboard?
Which brand produced the JX3P synth?
```
