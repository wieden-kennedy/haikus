"""
Classes and utilities for extracting haiku from arbitrary text and evaluating them based on some programmatically
defined criteria
"""
import nltk
import string
from nltk.corpus import cmudict
from nltk_util import syllables_en
from haikus.evaluators import DEFAULT_HAIKU_EVALUATORS

global WORD_DICT
try:
    WORD_DICT = cmudict.dict()
except LookupError:
    nltk.download('cmudict')
    WORD_DICT = cmudict.dict()

class NonwordError(Exception):
    pass

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

    def filtered_word(self, word):
        """
        Strip punctation from the given token so we can look it up in
        our word dictionary
        """
        exclude = set(string.punctuation).difference(set("'"))
        filtered = ''.join(ch for ch in word if ch not in exclude)
        return filtered
    
    def word_syllables(self, word, override_word=None):
        """
        Get the syllable count for the given word, according to WORD_DICT
        """
        word = word.encode('ascii', 'ignore').strip().lower()
        try:
            matches = WORD_DICT[word]
            for tree in matches:
                return (len([phoneme for phoneme in tree if phoneme[-1].isdigit()]), word)
        except KeyError:
            return self.unknown_word_handler(word)

    def syllable_map(self):
        """
        Map words in this text to their syllable count
        """
        s = self.filtered_text()
        try:
            return map(self.word_syllables, s.split())
        except NonwordError:
            return []
                
    def syllable_count(self):
        """
        Sum the syllable counts for all words in this text
        """
        return sum([t[0] for t in self.syllable_map()])

    def get_haiku(self):
        """
        find a haiku at the beginning of the text
        """
        syllable_map = self.syllable_map()
        return self.find_haiku(syllable_map)

    def get_haikus(self):
        """
        find all haikus in the text
        """
        haikus = []
        syllable_map = self.syllable_map()

        for i in range(len(syllable_map)):
            portion = syllable_map[i:]
            if (sum(word[0] for word in portion) >= 17):
                haiku = self.find_haiku(portion)
                if haiku:
                    haikus.append(haiku)
            else:
                break
        return haikus

    def find_haiku(self, syllable_map):
        """
        Find a haiku in this text
        """
        haiku = [5, 12, 17]
        cumulative = [0]
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
            haiku = Haiku()
            haiku.set_lines(lines)
            return haiku
        else:
            return False
        
    def has_haiku(self):
        """
        Return True if this text contains a haiku
        """
        return self.get_haiku() is not False

    def unknown_word_handler(self, word):
        """
        handle words outside of cmudict by attempting to count their syllables
        """
        syllable_count = syllables_en.count(self.filtered_word(word))
        if syllable_count > 0:
            return (syllable_count, word)
        else:
            raise NonwordError("%s has no syllables" % word)


class Haiku(object):
    """
    A simple wrapper for a haiku's three lines
    """
    def get_lines(self):
        return self._lines

    def set_lines(self, lines):
        self._lines = lines
    
    def calculate_quality(self, evaluators=None):
        """
        Calculate this haiku's quality
        """
        score = 0
        for evaluator_class, weight in evaluators:
            evaluator = evaluator_class(weight=weight)
            score += evaluator(self)
        try:
            score /= sum([weight for evaluator, weight in evaluators])
        except ZeroDivisionError:
            pass
        return score

    def line_end_bigrams(self):
        """
        Find the bigrams that occur across any two lines in this text's
        haiku
        """
        bigrams = ()
        lines = [line.split(" ") for line in self.get_lines()]
        try:
            bigrams = ((lines[0][-1],lines[1][0]),
                       (lines[1][-1],lines[2][0]))
        except IndexError:
            return (['', ''], ['', ''])
        return bigrams

    def flattened_lines(self):
        return ' '.join(self.get_lines())
