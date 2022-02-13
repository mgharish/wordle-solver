#!/usr/bin/python

import argparse
import logging
import re
import traceback


logging.basicConfig(level=logging.DEBUG) 

log_choices = {'CRITICAL':50, 'ERROR':40, 'WARNING':30,'INFO':20,'DEBUG':10}
alphabets = 'abcdefghijklmnopqrstuvwxyz'

# File with words 
dictionary_file = './words_alpha.txt'

indicators = {
        'correct' : '.',   # Character present at this position
        'absent' : '-',    # Character not present at this position
        'elsewhere' : '?'  # Character present, but not at this position
        }

def validate(guess_words, length):
    validated_words = []
    for w in guess_words:
        if(len(w) != length*2):
            raise Exception("Guess word '{}' is not formatted properly. It should have {} characters. Pleae check help".format(w, length*2))
        elif(not w[::2].isalpha()):
            raise Exception("Guess Word '{}' is not a proper word. Pleae check help".format(w))
        elif(not all(l in indicators.values() for l in w[1::2])):
            raise Exception("Guess Word '{}' has invalid qualifier characters. Pleae check help".format(w))
        else:
            validated_words.append((w[::2], w[1::2]))
    return validated_words
    
def get_words_of_length(filename, length):
    with open(filename) as f:
        lines = f.read().splitlines()
    
    return [w for w in lines if len(w)==length]

def solve(length=5, guess_words=[]):
    logger.debug('Validating guess words')
    guess_words = validate(guess_words, length) 

    logger.debug('Guess words: ' + str(guess_words))

    valid_words = get_words_of_length(dictionary_file, length)
    valid_chars = [alphabets] * length
    occurrences = {c:0 for c in alphabets}
    max_occurrences = {c:length for c in alphabets}

    for (w, q) in guess_words:
        logger.debug('Parsing word {} with qualifier {}'.format(w,q))
        for i in range(length):
            if(q[i] == indicators['correct']):
                occurrences[w[i]] += 1
                valid_chars[i] = w[i]
            if(q[i] == indicators['elsewhere']):
                occurrences[w[i]] += 1
                valid_chars[i] =  valid_chars[i].replace(w[i],'') 
            if(q[i] == indicators['absent']):
                max_occurrences[w[i]] = sum([1 if( w[i]==w[j] and q[j]!=indicators['absent']) else 0 for j in range(length)])
                logger.debug('Max occur of {} is {}'.format(w[i] ,max_occurrences[w[i]]))
                valid_chars = [vc.replace(w[i],'') if (max_occurrences[w[i]] == 0 and len(vc) != 1) else vc for vc in valid_chars]
                valid_chars[i] =  valid_chars[i].replace(w[i],'') 
            logger.debug('Valid characters: ' + str(valid_chars))

        pattern = ''.join([str('['+vc+']') for vc in valid_chars])
        r = re.compile(pattern)
        logger.debug('Filtering words with characters pattern {} '.format(pattern))
        valid_words = list(filter(r.match, valid_words))
        logger.debug('Valid words: ' + str(valid_words[:100]))

        logger.debug('Occurrences {}'.format(occurrences))
        logger.debug('Max occurrences {}'.format(max_occurrences))
        for k,v in occurrences.items():
            if v>0:
                if(max_occurrences[k] == v):
                    pattern  ='^[^'+k+']*' + '.*'.join(k*v) + '[^'+k+']*$'
                else:
                    pattern  ='^.*' + '.*'.join(k*v) + '.*$'
                logger.debug('Filtering words with pattern {} '.format(pattern))
                r = re.compile(pattern)
                valid_words = list(filter(r.match, valid_words))
                logger.debug('Valid words: ' + str(valid_words[:100]))
        occurrences = { k:0 for (k,v) in occurrences.items()}


    logger.debug('Valid characters: ' + str(valid_chars))
    logger.info('Valid words: ' + str(valid_words[:100]))
    
def setup_parser():
    parser = argparse.ArgumentParser(description='Guess Wordle word')
    parser.add_argument('guess_words', metavar='word', type=str, nargs='*',
            help='list of strings already guessed, with each character followed by one of the qualifier characters. {} indicates that the character does not exist, {} indictes that the character exists, but not in this spot and {} indicates that the character exists in this spot. For example: w{}o{}r{}d{} indicates that the charcters w and o do not exist in the given spots and r is present and is in the correct spot and d is in the word, but not in the correct spot'.format(indicators['absent'], indicators['elsewhere'], indicators['correct'], indicators['absent'], indicators['absent'], indicators['correct'], indicators['elsewhere'])
                        )
    parser.add_argument('-n', '--length', dest='length', default=5, type=int,
            help='length of each word (default: %(default)s)')
    parser.add_argument('-l', '--log-level', dest='log', choices=log_choices.keys(), default='INFO',
            help='set log level (default: %(default)s)')
    
    args = parser.parse_args()
    return parser, args



def setup_logger(level):
    logger = logging.getLogger(__name__)
    logger.propagate = False
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(fmt=formatter)
    handler.setLevel(level)
    logger.addHandler(handler)

    return logger

(parser, args) = setup_parser() 
logger = setup_logger(args.log)

logger.info('Solving Wordle game of {} characters'.format(args.length))


try:
    solve(args.length, args.guess_words)
except Exception as e:
    if(type(e) == 'Exception'):
        logger.critical('\n{}\n**********\n'.format(e))
    else:
        traceback.print_exc()
        
    parser.print_help()

