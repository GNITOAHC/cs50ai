import nltk
import sys
import os
import string
import math

nltk.download('stopwords')

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """

    file = dict()

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        # Check if filename ends with .txt
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), "r") as f:
                file[filename] = f.read()
    return file


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    # Tokenize document string and convert to lowercase
    tokens = nltk.word_tokenize(document.lower())

    # Remove punctuation and stopwords
    words = [word for word in tokens if word not in string.punctuation and word not in nltk.corpus.stopwords.words("english")]

    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idf = dict()

    # Get unique words from all documents
    unique_words = []
    for vocabulary in documents.values():
        unique_words.extend(set(vocabulary))
    unique_words = set(unique_words)

    # Calculate IDF for each word
    for word in unique_words:
        count = 0
        for vocabulary in documents.values():
            if word in vocabulary:
                count += 1
        idf[word] = math.log(len(documents) / count)

    return idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    # Calculate TF-IDF for each file
    tf_idf = dict()
    for filename, filecontent in files.items():
        file_score = 0
        for word in query:
            if word in filecontent:
                file_score += filecontent.count(word) * idfs[word]
            if file_score != 0:
                tf_idf[filename] = file_score

    # Sort files by TF-IDF score
    sorted_files = [k for k, _ in sorted(tf_idf.items(), key=lambda item: item[1], reverse=True)]
    return sorted_files[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    
    # Calculate IDF for each sentence
    idf = dict()
    for sentence, sentence_words in sentences.items():
        sentence_score = 0
        for word in query:
            if word in sentence_words:
                sentence_score += idfs[word]
        if sentence_score != 0:
            idf[sentence] = (sentence_score, sum([sentence_words.count(x) for x in query]) / len(sentence_words))

    # Sort sentences by IDF score
    sorted_sentences = [k for k, _ in sorted(idf.items(), key=lambda item: (item[1][0], item[1][1]), reverse=True)]

    return sorted_sentences[:n]


if __name__ == "__main__":
    main()
