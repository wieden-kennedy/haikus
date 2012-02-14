"""
Classes and utilities for extracting haiku from arbitrary text and evaluating them based on some programmatically
defined criteria
"""
import nltk
import string
from nltk.corpus import cmudict
from haikus.evaluators import DEFAULT_HAIKU_EVALUATORS

global WORD_DICT
WORD_DICT = cmudict.dict()


class HaikuText(object):
    """
    A wrapper around some sequence of text
    """
    def __init__(self, text=None):
        self._text = text
        
    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

    def filtered_text(self):
        """
        Strip punctuation from this text
        """
        exclude = set(string.punctuation).difference(set("'"))
        s = ''.join(ch for ch in self.get_text() if ch not in exclude)
        return s
    
    def word_syllables(self, word, override_word=None):
        """
        Get the syllable count for the given word, according to WORD_DICT
        """
        word = word.encode('ascii', 'ignore').strip().lower()
        matches = WORD_DICT[word]
        for tree in matches:
            return (len([phoneme for phoneme in tree if phoneme[-1].isdigit()]), word)

    def syllable_map(self):
        """
        Map words in this text to their syllable count
        """
        s = self.filtered_text()
        try:
            return map(self.word_syllables, s.split())
        except KeyError, e:
            return []
        
    def syllable_count(self):
        """
        Sum the syllable counts for all words in this text
        """
        return sum([t[0] for t in self.syllable_map()])

    def line_end_bigrams(self):
        """
        Find the bigrams that occur across any two lines in this text's
        haiku
        """
        bigrams = ()
        if self.has_haiku():
            lines = [line.split(" ") for line in self.haiku()]
            bigrams = ((lines[0][-1], lines[1][0]), (lines[1][-1], lines[2][0]))
        return bigrams
    
    def haiku(self):
        """
        Find a haiku in this text
        """
        haiku = [5, 12, 17]
        cumulative = [0]
        syllable_map = self.syllable_map()
        for w in syllable_map:
            cumulative.append(cumulative[-1] + w[0])
        cumulative = cumulative[1:]
        is_haiku = set(cumulative).intersection(haiku) == set(haiku)
        
        if is_haiku:
            lookup = dict((v,k) for k, v in enumerate(cumulative))
            enum_lookup = list(enumerate(lookup))
            start = 0
            lines = []
            for line in haiku:
                section = syllable_map[start:lookup[line]+1]
                words = [s[1] for s in section]
                lines.append(' '.join(words))
                try:
                    start = enum_lookup[lookup[line] + 1][0]
                except IndexError:
                    pass
            return lines
        else:
            return False
        
    def has_haiku(self):
        """
        Return True if this text contains a haiku
        """
        return bool(self.haiku())
    
    def calculate_quality(self, evaluators=None):
        """
        Calculate the score of this text's haiku across a list of evaluators
        and return the mean average.
        """
        if evaluators is None:
            evaluators = DEFAULT_HAIKU_EVALUATORS
        score = 0
        if self.has_haiku():
            for evaluator_class, weight in evaluators:
                evaluator = evaluator_class(weight=weight)
                score += evaluator(self)
            try:
                score /= sum([weight for evaluator, weight in evaluators])
            except ZeroDivisionError:
                return 0
        return score
