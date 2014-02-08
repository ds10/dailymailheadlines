from collections import defaultdict, Counter
import random
import operator
import re
from nltk import bigrams
from nltk.corpus import stopwords
import requests

RSS_URLS = ('http://www.dailymail.co.uk/news/index.rss',
            'http://www.dailymail.co.uk/tvshowbiz/index.rss',
            'http://www.dailymail.co.uk/femail/index.rss')
TITLE_SIZE = 15
BAD_CHARS = (')', ':', '"', '\'')


def _get_headlines():
    """ Gather a list of headlines from the RSS feeds """
    rss_string = ' '.join([requests.get(url).content for url in RSS_URLS])
    headlines = set(re.findall('<title>(.+)</title>', rss_string))
    # filter out any headlines containing disallowed chars
    return [h for h in headlines if not any(sym in h for sym in BAD_CHARS)]


def _remove_stop_words(word_list):
    """ Remove stop words from the end of a list of words """
    if word_list[len(word_list) - 1] in set(stopwords.words('english')):
        del word_list[len(word_list) - 1]
        _remove_stop_words(word_list)
    return word_list


def _convert_all_caps(word_list):
    """ Convert any ALLCAPS words in a list to lower """
    return [w.lower() if w.isupper() else w for w in word_list]


def _find_bigrams(headlines):
    tokens = " ".join(headlines).split()
    bigs = bigrams(tokens)
    # return bigrams dict with count, sorted descending
    return sorted(Counter(bigs).items(),
                  key=operator.itemgetter(1), reverse=True)


def generate_title():
    headlines = _get_headlines()
    bigs_sorted = _find_bigrams(headlines)

    # convert bigrams sorted list to dict
    bigs_dict = defaultdict(list)
    for ((big_key, words_list), count) in bigs_sorted:
        bigs_dict[big_key].append(words_list)

    bigs_choices = (' ',)
    while len(bigs_choices[0]) < TITLE_SIZE / 2 and \
            not bigs_choices[0][0][0].isupper():  # first letter is not upper
        # get possible next words list
        bigs_choices = [i[0] for i in bigs_sorted]
        random.shuffle(bigs_choices)

    title_words = []
    # set the first key word to start
    key_word = bigs_choices[0][0]
    title_words.append(key_word)

    while len(title_words) < TITLE_SIZE:
        # get possible next words for a given bigram key
        next_word_list = bigs_dict.get(key_word)
        if not next_word_list:
            continue
        key_word = random.choice(next_word_list)
        title_words.append(key_word)

    title_words = _remove_stop_words(title_words)
    title_words = _convert_all_caps(title_words)
    return " ".join(title_words).capitalize()
