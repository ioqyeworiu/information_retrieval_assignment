from pydantic import BaseModel
from numpy import log
from index_module.inverted_index import InvertedIndex

def compute_idf(inverted_index: dict[str, list[int]], total_documents: int) -> dict[str, float]:
    idf = {}
    for word, doc_ids in inverted_index.items():
        n = len(doc_ids)
        idf[word] = log(((total_documents - n + 0.5) / (n + 0.5)) + 1)
    return idf

def count_term_frequency(documents: list[tuple[str, str]]) -> dict[str, dict[str, int]]:
    tf = {}
    for doc_id, text in documents:
        tf[doc_id] = {}
        for word in text.split():
            tf[doc_id][word] = tf[doc_id].get(word, 0) + 1
    return tf


class Bm25Okapi(BaseModel):
    k1: float = 1.5
    b: float = 0.75
    freq: dict[str, dict[str, int]] = {}
    inverted_index: dict[str, list[int]] = {}
    idf: dict[str, float] = {}
    avgdl: float = 0.0

    def fit(self, documents: list[tuple[str, str]], k1: float, b: float) -> dict[str, float]:
        self.k1 = k1
        self.b = b
        self.freq = count_term_frequency(documents)
        self.inverted_index = InvertedIndex.build(documents)
        self.idf = compute_idf(self.inverted_index, len(documents))
        self.avgdl = sum(len(doc[1].split()) for doc in documents) / len(documents)

    def scores(self, query: str) -> dict[str, float]:
        scores = {}
        for doc in self.freq:
            score = 0.0
            for word in query.split():
                if word in self.freq[doc].keys():
                    tf = self.freq[doc][word]
                    idf = self.idf.get(word, 0.0)
                    dl = sum(self.freq[doc].values())
                    score += idf * ((tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * (dl / self.avgdl))))
            scores[doc] = score
        return scores