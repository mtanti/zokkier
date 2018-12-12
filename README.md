# zokkier (version 0.1)
A simple stemmer for Maltese words (Malti).

Current accuracy: 61.9%

This stemmer was developed in Python 3 using a greedy algorithm which chops off the longest known prefixes and suffixes. The prefixes and suffixes are extracted from a training set which consists of words from the Ġabra lexicon that have been manually segmented by a single non-linguist (hopefully later versions of this stemmer will be collaborative). This means that accuracy is not guaranteed. Below for guidelines used.

Stemming consists of removing a prefix and a suffix. No further charges are made to the word.

## Training sets
There are 2 training sets consisting of the different word forms of 100 different randomly selected lemmas (a lemma includes all words with same root) from Ġabra 2015-11-19 (http://mlrs.research.um.edu.mt/resources/gabra-api/download)

Script to generate raw words used for training sets in trainingset_tools.py. Each training set sample is generated using a known seed to be able to regenerate the words.

Stemming was done manually and consists of hyphens to separate the prefix and the suffix from the stem.

Guidelines:
- The word radicals/roots are used to determine where the stem begins and ends.
- Weak consonants at the end of the radicals are ignored as they occur in bound morphemes ("wela" w-l-j was also done this way for consistency even though the "j" is consistently used as a radical throughout the word group).
- No semitic stem can begin or end with a vowel and no stem can begin or end with a double letter.
- A number of non-semitic word groups consist of 3 words that either end in "ika", "iku", "iċi", or in "", "a", "i". These are always split in order to have these suffixes.

## Known affixes
Since the stemming algorithm works by chopping off known suffixes and prefixes, a list of known suffixes and prefixes needs to be generated. This is done by extracting them from the training set if they exceed a certain frequency. It was found that filtering by frequency only reducing the accuracy of the stemmer so no filtering was done. See graph of how the accuracy changes as the minimum frequency is changed.
