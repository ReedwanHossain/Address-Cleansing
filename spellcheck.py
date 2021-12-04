# import the fuzzywuzzy module


from fuzzywuzzy import fuzz
import enchant

# spellcheck main class


class SpellCheck:

    # initialization method
    def __init__(self, word_dict_file=None):
        # open the dictionary file
        self.file = open(word_dict_file, 'r')

        # load the file data in a variable
        data = self.file.read()

        # store all the words in a list
        data = data.split(",")

        # change all the words to lowercase
        data = [i.lower() for i in data]

        # remove all the duplicates in the list
        data = set(data)

        # store all the words into a class variable dictionary
        self.dictionary = list(data)

    # string setter method
    def check(self, string_to_check):
        # store the string to be checked in a class variable
        self.string_to_check = string_to_check

    # this method returns the possible suggestions of the correct words
    def suggestions(self):
        # store the words of the string to be checked in a list by using a split function
        string_words = self.string_to_check.split()

        # a list to store all the possible suggestions
        suggestions = []

        # loop over the number of words in the string to be checked
        for i in range(len(string_words)):

            # loop over words in the dictionary
            for name in self.dictionary:

                # if the fuzzywuzzy returns the matched value greater than 80
                if fuzz.ratio(string_words[i].lower().strip(), name.lower()) >= 90:

                    # append the dict word to the suggestion list
                    suggestions.append(name)

        # return the suggestions list
        return suggestions

    # this method returns the corrected string of the given input
    def correct(self):
        # store the words of the string to be checked in a list by using a split function
        string_words = self.string_to_check.split()

        # loop over the number of words in the string to be checked
        for i in range(len(string_words)):

            # initiaze a maximum probability variable to 0
            max_percent = 0
            Dic = {}
            # loop over the words in the dictionary
            for name in self.dictionary:

                # calulcate the match probability
                if name[0] == string_words[i][0] and name[-1]==string_words[i][-1]:
                    percent = fuzz.ratio(
                        string_words[i].lower().strip(), name.lower())
                    # if the fuzzywuzzy returns the matched value greater than 80
                    if percent >= 80 and enchant.utils.levenshtein(string_words[i].lower().strip(), name.lower()) < 3:

                        # print string_words[i]+" : "+name+" : "+str(percent)
                        #string_words[i] = name
                        Dic.update({name: percent})

                        # if the matched probability is
                        if percent > max_percent:
                            max_percent = percent

                            # change the original value with the corrected matched value

                        # change the max percent to the current matched percent
            try:
                string_words[i] = max(Dic.keys(), key=(lambda k: Dic[k]))
            except:
                string_words[i] = string_words[i]
            # print Dic

        # return the cprrected string
        return " ".join(string_words)
