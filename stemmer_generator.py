##############################################################
def load_trainingset():
    '''
    Obtain a list of prefixes and suffixes from the segmented training set together with their frequencies.
    '''
    min_stem_len = 1000
    suffix_freqs = dict()
    prefix_freqs = dict()
    with open("trainingset1.txt", "r", encoding="utf-8") as f:
        for line in f:
            if line == "\n":
                continue
            
            (prefix, stem, suffix) = line.strip().split("-")
            
            #Process stem
            
            if len(stem) < min_stem_len:
                min_stem_len = len(stem)
            
            #Process prefix
            if len(prefix) > 0:
                if prefix[-1] == stem[0]:
                    prefix = prefix[:-1] #remove the last letter from a prefix if it is due to a doubled first letter in the stem as that is handled in post processing
                if len(prefix) > 0:
                    if prefix not in prefix_freqs:
                        prefix_freqs[prefix] = 1
                    else:
                        prefix_freqs[prefix] += 1

            #Process suffix
            if len(suffix) > 0:
                if stem[-1] == suffix[0]:
                    suffix = suffix[1:] #remove the first letter from a suffix if it is due to a doubled last letter in the stem as that is handled in post processing
                if len(suffix) > 0:
                    if suffix not in suffix_freqs:
                        suffix_freqs[suffix] = 1
                    else:
                        suffix_freqs[suffix] += 1

    return (min_stem_len, prefix_freqs, suffix_freqs)

    
##############################################################
def load_testset():
    '''
    Obtain a list of words together with their correct segmentation from the segmented test set.
    '''
    test_set = []
    with open("trainingset2.txt", "r", encoding="utf-8") as f:
        for line in f:
            if line == "\n":
                continue
            
            (prefix, stem, suffix) = line.strip().split("-")
            word = prefix + stem + suffix
            test_set.append((word, (prefix, stem, suffix)))
    
    return test_set
    
##############################################################
class Stemmer():

    def __init__(self, prefix_freqs, suffix_freqs, min_freq, min_stem_len):
        self.prefixes = { prefix for prefix in prefix_freqs.keys() if prefix_freqs[prefix] >= min_freq }
        self.suffixes = { suffix for suffix in suffix_freqs.keys() if suffix_freqs[suffix] >= min_freq }
        self.min_stem_len = min_stem_len
        
    def stem(self, word):
        word_len = len(word)

        if word_len <= self.min_stem_len:
            return word

        for suffix_len in range(word_len-self.min_stem_len, 0, -1):
            suffix = word[-suffix_len:]
            if suffix in self.suffixes:
                if word[-suffix_len] == word[-suffix_len-1]: #remove doubled letter
                    suffix_len += 1
                word = word[:-suffix_len]
                word_len = len(word)
                break
            
        for prefix_len in range(word_len-self.min_stem_len, 0, -1):
            prefix = word[:prefix_len]
            if prefix in self.prefixes:
                if word[prefix_len-1] == word[prefix_len]: #remove doubled letter
                    prefix_len += 1
                word = word[prefix_len:]
                break
                
        return word

        
##############################################################
def evaluate(testset, stemmer):
    '''
    Evaluate a stemmer based on a test set of word/stem pairs.
    Return fraction of correct stemmings.
    '''
    num_correct = 0
    for (word, (prefix, stem, suffix)) in testset:
        predicted_stem = stemmer.stem(word)
        if predicted_stem == stem:
            num_correct += 1
    return num_correct/len(testset)

##############################################################
(min_stem_len, prefix_freqs, suffix_freqs) = load_trainingset()
testset = load_testset()
freqs = sorted(set(list(prefix_freqs.values()) + list(suffix_freqs.values())))

print("Searching for best minimum frequency from", freqs[0], "to", freqs[-1], "(", len(freqs), " different frequences)...")
print("Minimum frequency", "Stemming score (out of 1)", sep="\t")
best_min_freq = None
best_score = 0.0
for min_freq in freqs:
    print(min_freq, end="\t")
    stemmer = Stemmer(prefix_freqs, suffix_freqs, min_freq, min_stem_len)
    score = evaluate(testset, stemmer)
    print(score)
    if score > best_score:
        best_min_freq = min_freq
        best_score = score

print()
print("Best score:", round(best_score*100,2), "%")
print()
print("Stemmer:")
print("""
class Stemmer():

    def __init__(self):
        self.prefixes = """ + repr({ prefix for prefix in prefix_freqs.keys() if prefix_freqs[prefix] >= best_min_freq }) + """
        self.suffixes = """ + repr({ suffix for suffix in suffix_freqs.keys() if suffix_freqs[suffix] >= best_min_freq }) + """
        self.min_stem_len = """ + repr(min_stem_len) + """
        
    def stem(self, word):
        word_len = len(word)

        if word_len <= self.min_stem_len:
            return word

        for suffix_len in range(word_len-self.min_stem_len, 0, -1):
            suffix = word[-suffix_len:]
            if suffix in self.suffixes:
                if word[-suffix_len] == word[-suffix_len-1]: #remove doubled letter
                    suffix_len += 1
                word = word[:-suffix_len]
                word_len = len(word)
                break
            
        for prefix_len in range(word_len-self.min_stem_len, 0, -1):
            prefix = word[:prefix_len]
            if prefix in self.prefixes:
                if word[prefix_len-1] == word[prefix_len]: #remove doubled letter
                    prefix_len += 1
                word = word[prefix_len:]
                break
                
        return word
""")
