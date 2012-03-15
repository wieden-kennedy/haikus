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
    requires_punctuation = False
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
    
        for line in haiku:
            tagged_words = nltk.pos_tag(line.split())
            if nv_regex.match(tagged_words[-1][1]) is not None:
                score += 100
        score = score/len(haiku)
        return score

class JoiningWordLineEndingEvaluator(HaikuEvaluator):
    """
    If the line doesn't end in a preposition, in, and, or other
    joining words, boost its score
    """
    def evaluate(self, haiku):
        score = 0
        join_regex = re.compile("(^W.*$|IN|DT|CC|PRP\$|TO)")

        for line in haiku:
            tagged_words = nltk.pos_tag(line.split())
            if join_regex.match(tagged_words[-1][1]) is None:
                score += 100
        score = score/len(haiku)
        return score

class EndsInNounEvaluator(HaikuEvaluator):
    """
    If the entire haiku ends in a noun, boost its score.
    """
    def evaluate(self, haiku):
        score = 0
        noun_regex = re.compile("(^N.*$|PRP.*$)")
        line = haiku[-1]
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
        for line in haiku:
            nltk.pos_tag(line.split())
            [tags.append(tag) for word, tag in nltk.pos_tag(line.split())]
        found = [tag for tag in tags if tag in seeking]
        score = 100 - math.exp(len(found))
        if score < 0:
            return 0
        else:
            return score

class LineEndPunctuationEvaluator(HaikuEvaluator):
    """
    If a haiku's lines end in punctuation (,!?; or .) boost its score
    """
    requires_punctuation = True
    def evaluate(self, haiku):
        score = 0
        terminal_punctuation = set([',','!','?','.',';'])
        for line in haiku:
            if line[-1] in terminal_punctuation:
                score += 100
        return score/len(haiku)

class LineIsFullSentenceEvaluator(HaikuEvaluator):
    """
    If a line in a haiku is a full sentence, boost the score
    """
    requires_punctuation = True
    def evaluate(self, haiku):
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        score = 0
        for line in haiku:
            if line in sentence_tokenizer.tokenize(line):
                score += 100
        return score/len(haiku)
        
class HaikuIsFullSentenceEvaluator(HaikuEvaluator):
    """
    If the entire haiku forms a complete sentence, boost the score
    """
    def evaluate(self, haiku):
        score = 0
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        flat_haiku = '%s.'%' '.join(haiku)
        if flat_haiku in sentence_tokenizer.tokenize(flat_haiku):
            score += 100
        return score
        

DEFAULT_HAIKU_EVALUATORS = [
    (NounVerbAdjectiveLineEndingEvaluator, 1),
    (JoiningWordLineEndingEvaluator, 1),
    (EndsInNounEvaluator, 1),
    (PrepositionCountEvaluator, 1),
    (LineIsFullSentenceEvaluator, 1),
    (HaikuIsFullSentenceEvaluator, 1),
    (LineEndPunctuationEvaluator, 1),
]

HAIKU_EVALUATORS = [
    NounVerbAdjectiveLineEndingEvaluator,
    JoiningWordLineEndingEvaluator,
    EndsInNounEvaluator,
    PrepositionCountEvaluator,
    LineIsFullSentenceEvaluator,
    HaikuIsFullSentenceEvaluator,
    LineEndPunctuationEvaluator,
]
