import random
import pickle
import pymongo

##############################################################
def get_gabra_word_groups():
    '''
    Create a list of words obtained from a loaded Gabra MongoDB database and group them by lemma. Caches result into a pickle to avoid using the MongoDB database again.
    If you already have gabra.pkl available then you do not need to load the MongoDB database.
    
    Word groups list consists of the following tuples:
    [
        (
            lemma e.g. "kiser",
            root e.g. "k-s-r",
            wordforms e.g. [ "ksirt", "kiser", "kisret", ... ]
        ),
        ...
    ]
    '''
    try:
        with open("gabra.pkl", "rb") as f:
            return pickle.load(f)
    except:
        pass
    
    #To create a MongoDB instance with the Gabra dump:
    #download tar file from http://mlrs.research.um.edu.mt/resources/gabra-api/download and extract it into a folder X
    #in X create a folder called "data" next to "tmp"
    #open a cmd, change directory to X and load a mongodb instance using   mongod --dbpath data
    #open another cmd, change directory to X\tmp and restore the dump to the database in "data" using   mongorestore -d gabra --port 27017 gabra
    db = pymongo.MongoClient()
    invalid_vowel_pairs = { x+y for x in "aeiou" for y in "aeiou" } - { "ie", "oe", "ea", "ao", "oa", "eo" }
    is_valid_word = lambda word:not any(word[i:i+2] in invalid_vowel_pairs for i in range(len(word)-1)) and word.islower() and word.isalpha()
    is_valid_lexeme_doc = lambda lexeme:"lemma" in lexeme and not ("pending" in lexeme and lexeme["pending"]) and is_valid_word(lexeme["lemma"])
    added_roots = set()
    word_groups = []
    for lexeme in db["gabra"]["lexemes"].find():
        if not is_valid_lexeme_doc(lexeme):
            continue
        lexeme_id = lexeme["_id"]
        lemma = lexeme["lemma"]
        if "root" in lexeme and lexeme["root"] is not None and "radicals" in lexeme["root"]:
            root = lexeme["root"]["radicals"]
            if root in added_roots:
                continue
            else:
                added_roots.add(root)
            alternative_lemmas = { #all lemmas with same root
                (alt_lexeme["_id"], alt_lexeme["lemma"])
                for alt_lexeme in db["gabra"]["lexemes"].find({"root.radicals":root})
                if is_valid_lexeme_doc(alt_lexeme)
            }
            (lexeme_id, lemma) = min(alternative_lemmas, key=lambda x:len(x[1])) #use shortest lemma of alternatives to represent all lemmas
            wordforms = { #unify all word forms of all alternative lemmas
                wordform["surface_form"]
                for (alt_lexeme_id, alt_lemma) in alternative_lemmas
                for wordform in db["gabra"]["wordforms"].find({"lexeme_id":alt_lexeme_id})
                if is_valid_word(wordform["surface_form"])
            }
        else:
            root = ""
            wordforms = { #get all word forms of lemma
                wordform["surface_form"]
                for wordform in db["gabra"]["wordforms"].find({"lexeme_id":lexeme_id})
                if is_valid_word(wordform["surface_form"])
            }
        if len(wordforms) < 3:
            continue
        word_groups.append((lemma, root, sorted(wordforms)))
    word_groups.sort()
            
    with open("gabra.pkl", "wb") as f:
        pickle.dump(word_groups, f)

    return word_groups

##############################################################
def create_raw_trainingset():
    '''
    Generate random (based on seed) sample of word groups and split them into two equal halves of 100 groups each for two separate text files called "trainingset1.txt" and "trainingset2.txt".
    
    The idea is to have a text file of words which can be manually split into stems and affixes using a text editor.
    The two files are used for training and validation.
    '''
    random.seed(seed)
    pre_selected_word_groups = random.sample(word_groups, 200)
    random.shuffle(pre_selected_word_groups)
    for i in range(2):
        selected_word_groups = pre_selected_word_groups[100*(i+0):100*(i+1)]
        selected_word_groups.sort()
        with open("trainingset%s.txt"%(i+1,), "w", encoding="utf-8") as f:
            for (lemma, root, wordforms) in selected_word_groups:
                for word in wordforms:
                    print(word, file=f)
                print("", file=f)


##############################################################
def get_trainingset_roots():
    '''
    Take the training sets generated by the previous function and display their roots in order to help decide where the segmentation should be applied.
    '''
    random.seed(seed)
    pre_selected_word_groups = random.sample(word_groups, 200)
    random.shuffle(pre_selected_word_groups)
    for i in range(2):
        print("trainingset%s.txt"%(i+1,))
        selected_word_groups = pre_selected_word_groups[100*(i+0):100*(i+1)]
        selected_word_groups.sort()
        for (lemma, root, wordforms) in selected_word_groups:
            print(lemma, root)
        print()
        

##############################################################
def validate_trainingset():
    '''
    Validate the manually segmented words in trainingset1.txt and trainingset2.txt.
    The following validations are applied:
        Check that, ignoring segmentation, the files still contain the same words generated in create_raw_trainingset().
        Check that there are exactly 3 segments (separated by a "-") in each word.
        Check that the stem (middle segment) does not end in a vowel as it was observed that no stem in Maltese ends in a vowel.
    '''
    random.seed(seed)
    pre_selected_word_groups = random.sample(word_groups, 200)
    random.shuffle(pre_selected_word_groups)
    for i in range(2):
        print("trainingset%s.txt"%(i+1,))
        selected_word_groups = pre_selected_word_groups[100*(i+0):100*(i+1)]
        selected_word_groups.sort()
        originals = [ word for (lemma, root, wordforms) in selected_word_groups for word in wordforms+[ "" ] ]
        with open("trainingset%s.txt"%(i+1,), "r", encoding="utf-8") as f:
            for (line, original) in zip(f, originals):
                line = line.strip("\r\n")
                if line.replace("-", "") != original:
                    print("corrupted word", line, "should be", original)
                    break #break as a corrupted word might be caused by a missing or extra line which would shift all following words making them all appear corrupted.
                elif line != "":
                    if line.count("-") != 2:
                        print("segments", line)
                    else:
                        (prefix, stem, suffix) = line.split("-")
                        if stem[-1] in { "a", "e", "i", "o", "u" }:
                            print("vowel", line)
        print()

                            
##############################################################
#obtain word groups from MongoDB database or cached gabra.pkl
word_groups = get_gabra_word_groups()

seed = 1

#uncomment the function call you want to execute

#create_raw_trainingset()
#get_trainingset_roots()
validate_trainingset()
