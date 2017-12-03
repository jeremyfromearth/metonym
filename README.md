# metonym
Domain specific language for generating analogous variations of textual inputs

### Grammar:
__Symbols__
```
LBRACKET = [
RBRACKET = ] 
LPAREN = (
RPAREN = )
COLON = :
```
__Rules__
```
expression = string, optional, required, {string | optional | required}
requried = '[' (string, entity, optional) ']';
optional = '(' (string '|' optional) ')';
string = term, {term};
entity = term ':' term
term = char, {char};
char = \[a-Z]\;
```
### Example
Consider the excerpt from the Wikipedia article for Roland JX3P...
> The Roland JX-3P is a synthesizer produced by Roland Corporation of Japan in 1983. .  
... and the various ways in which one could ask the question the question "Who made the JX-3P?"..

Below is an example of a command that creates 79 analogous variations of the simple question above.
```
[Who:make | [What | which] [company | brand)]:make] [created|built|designed|made] the [JX-3P (synthesizer | keyboard | synth)]:model?
```
... the 79 variations
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
Who made the JX3P?
Who made the JX3P synthesizer?
Who made the JX3P keyboard?
Who made the JX3P synth?
What company made the JX3P?
What company made the JX3P synthesizer?
What company made the JX3P keyboard?
What company made the JX3P synth?
What brand made the JX3P?
What brand made the JX3P synthesizer?
What brand made the JX3P keyboard?
What brand made the JX3P synth?
Which company made the JX3P?
Which company made the JX3P synthesizer?
Which company made the JX3P keyboard?
Which company made the JX3P synth?
Which brand made the JX3P?
Which brand made the JX3P synthesizer?
Which brand made the JX3P keyboard?
Which brand made the JX3P synth?
```
