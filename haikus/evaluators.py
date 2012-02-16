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
        
    def __call__(self, comment):
        return self.weight * self.evaluate(comment)

    def pre_evaluate(self):
        pass

    def evaluate(self, comment):
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
    def evaluate(self, comment):
        score = 0
        nv_regex = re.compile("(^N.*|^V.*|^J.*)")
        lines = comment.haiku(strip_punctuation=True)

        if lines:
            for line in lines:
                tagged_words = nltk.pos_tag(line.split())
                print tagged_words
                print tagged_words[-1][1]
                if nv_regex.match(tagged_words[-1][1]) is not None:
                    score += 100
            score = score/len(lines)
        return score

class JoiningWordLineEndingEvaluator(HaikuEvaluator):
    """
    If the line doesn't end in a preposition, in, and, or other
    joining words, boost its score
    """
    def evaluate(self, comment):
        score = 0
        join_regex = re.compile("(^W.*$|IN|DT|CC|PRP\$|TO)")

        lines = comment.haiku()

        if lines:
            for line in lines:
                tagged_words = nltk.pos_tag(line.split())
                if join_regex.match(tagged_words[-1][1]) is None:
                    score += 100
            score = score/len(lines)
        return score

class EndsInNounEvaluator(HaikuEvaluator):
    """
    If the entire haiku ends in a noun, boost its score.
    """
    def evaluate(self, comment):
        score = 0
        noun_regex = re.compile("(^N.*$|PRP.*$)")
        lines = comment.haiku(strip_punctuation=True)
        line = lines[-1]
        tagged_words = nltk.pos_tag(line.split())
        if noun_regex.match(tagged_words[-1][1]) is not None:
            score = 100
        return score

class PrepositionCountEvaluator(HaikuEvaluator):
    """
    If the entire haiku ends in a noun, boost its score.
    """
    def evaluate(self, comment):
        lines = comment.haiku(strip_punctuation=True)
        tags = []
        seeking = ['IN']
        for line in lines:
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
    def evaluate(self, comment):
        score = 0
        terminal_punctuation = set(',','!','?','.',';')
        lines = comment.haiku()
        for line in lines:
            if line[-1] in terminal_punctuation:
                score += 100
        return score/len(lines)

class LineIsFullSentenceEvaluator(HaikuEvaluator):
    """
    If a line in a haiku is a full sentence, boost the score
    """
    def evaluate(self, comment):
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        score = 0
        lines = comment.haiku()
        for line in lines:
            if line in sentence_tokenizer.tokenize(line):
                score += 100
        return score/len(lines)


class HaikuIsFullSentenceEvaluator(HaikuEvaluator):
    """
    If the entire haiku forms a complete sentence, boost the score
    """
    def evaluate(self, comment):
        score = 0
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        haiku = ' '.join(comment.haiku())
        if haiku in sentence_tokenizer.tokenize(haiku):
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
