#Haikus
Haikus is a Python library for finding haikus in arbitrary text using NLTK.
It simply finds 5 and 7 syllable phrases that form haikus in a 5,7,5 pattern.

##Installation
Use pip!
```python
pip install -e git+https://github.com/wieden-kennedy/haikus#egg=haikus
```

##Usage
It's easy to find haikus in text with Haikus.
Simply instantiate a HaikuText object with your choice of text and ask it to find haikus.
```python
from haikus import HaikuText

f = open("/tmp/my_term_paper.txt", "r")
text = HaikuText(text=f.read())

haikus = HaikuText.get_haikus()
```

HaikuText's get_haikus() function will return a Haiku instance for every haiku in the text.
Haiku's get_lines() method will return a list of lines in the haiku.
```python
haiku = haikus[0]

print haiku.get_lines()
# oh look, a haiku from your term paper! ["abraham lincoln", "was a president one time", "he freed many slaves"]
```

##Haiku Evaluation
Haikus includes functions for evaluating Haiku objects based on their contents.  Haiku's calculate_quality() method will
calculate the quality of a Haiku instance based on a set of evaluators. You can use the set of weighted evaluators provided by
Haikus or create your own set of weighted evaluators.

```python
haiku.calculate_quality()
# this will return the haiku's quality according to the DEFAULT_HAIKU_EVALUATORS

MY_RAD_EVALUATORS = [
  #look at these evaluator, weight tuples!
  (IsAwesomeEvaluator, 1),
  (ContainsDogEvaluator, 0.75),
]
haiku.calculate_quality(evaluators=MY_RAD_EVALUATORS)
#this will calculate the quality accordin to MY_RAD_EVALUATORS
```

You can create your own evaluators by inheriting from ```haiku.evaluators.HaikuEvaluator``` and implementing the
evaluate() method. See ```haiku.evaluators``` for some examples.

For more usage examples, see the tests, or check out [Django-Haikus](https://github.com/wieden-kennedy/django-haikus/)

