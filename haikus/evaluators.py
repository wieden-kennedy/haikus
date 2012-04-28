"""
Simple haiku evaluators. Callables that give a score (out of 100) to a
haiku based on some criteria.
"""
import re, math
import nltk
import nltk.collocations
from nltk.classify import NaiveBayesClassifier

class HaikuEvaluator(object):
    """
    Base HaikuEvaluator -- simply a callable class
    with weight and an evaluate method
    """
    def __init__(self, weight=1):
        self.weight = weight
        self.pre_evaluate()
        
    def __call__(self, haiku):
        return self.weight * self.evaluate(haiku)

    def pre_evaluate(self):
        pass

    def evaluate(self, haiku):
        """
        Evaluate a comment. Override this in
        subclasses.
        """
        return 100
    
class NounVerbAdjectiveLineEndingEvaluator(HaikuEvaluator):
    """
    Analyze the part of speech of each line ending,
    boost lines ending in nouns or verbs.

    Returns 0 - 100
    """
    def evaluate(self, haiku):
        score = 0
        nv_regex = re.compile("(^N.*|^V.*|^J.*)")
    
        for line in haiku.get_lines():
            tagged_words = nltk.pos_tag(line.split())
            if nv_regex.match(tagged_words[-1][1]) is not None:
                score += 100
        score = score/len(haiku.get_lines())
        return score

class JoiningWordLineEndingEvaluator(HaikuEvaluator):
    """
    If the line doesn't end in a preposition, in, and, or other
    joining words, boost its score
    """
    def evaluate(self, haiku):
        score = 0
        join_regex = re.compile("(^W.*$|IN|DT|CC|PRP\$|TO)")

        for line in haiku.get_lines():
            tagged_words = nltk.pos_tag(line.split())
            if join_regex.match(tagged_words[-1][1]) is None:
                score += 100
        score = score/len(haiku.get_lines())
        return score

class EndsInNounEvaluator(HaikuEvaluator):
    """
    If the entire haiku ends in a noun, boost its score.
    """
    def evaluate(self, haiku):
        score = 0
        noun_regex = re.compile("(^N.*$|PRP.*$)")
        line = haiku.get_lines()[-1]
        tagged_words = nltk.pos_tag(line.split())
        if noun_regex.match(tagged_words[-1][1]) is not None:
            score = 100
        return score

class PrepositionCountEvaluator(HaikuEvaluator):
    """
    If the entire haiku ends in a noun, boost its score.
    """
    def evaluate(self, haiku):
        tags = []
        seeking = ['IN']
        [tags.append(tag) for word, tag in nltk.pos_tag(haiku.flattened_lines().split())]
        
        found = [tag for tag in tags if tag in seeking]
        score = 100 - math.exp(len(found))
        if score < 0:
            return 0
        else:
            return score
        
DEFAULT_HAIKU_EVALUATORS = [
    (NounVerbAdjectiveLineEndingEvaluator, 1),
    (JoiningWordLineEndingEvaluator, 1),
    (EndsInNounEvaluator, 1),
    (PrepositionCountEvaluator, 1),
]

HAIKU_EVALUATORS = [
    NounVerbAdjectiveLineEndingEvaluator,
    JoiningWordLineEndingEvaluator,
    EndsInNounEvaluator,
    PrepositionCountEvaluator,
]
