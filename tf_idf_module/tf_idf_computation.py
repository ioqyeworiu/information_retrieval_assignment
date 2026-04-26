from index_module.inverted_index import InvertedIndex
from numpy import log



def compute_idf(inverted_index: InvertedIndex, total_documents: int) -> dict[str, float]:
    idf = {}
    for term, doc_ids in inverted_index.items():
        idf[term] = log((1 + total_documents) / (1 + len(doc_ids))) + 1  #smoot
    return idf

def compute_tf(document: str) -> dict[str, float]:
    tf = {}
    words = document.split()
    total_words = len(words)
    for word in words:
        tf[word] = tf.get(word, 0) + 1
    for word in tf:
        tf[word] /= total_words
    return tf
