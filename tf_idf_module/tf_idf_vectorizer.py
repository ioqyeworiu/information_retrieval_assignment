from pydantic import BaseModel, Field
from index_module.inverted_index import InvertedIndex
from tf_idf_module import tf_idf_computation


class TFIDFVectorizer(BaseModel):
    inverted_index: InvertedIndex = Field(default=dict())
    idf: dict[str, float] = Field(default=dict())

    def fit(self, documents: list[tuple[str, str]]):
        self.inverted_index = InvertedIndex.build(documents)
        self.idf = tf_idf_computation.compute_idf(self.inverted_index, len(documents))

    def transform(self, documents: list[tuple[str, str]]) -> dict[str, dict[str, float]]:
        tf_idf_vectors = {}
        for doc_id, document in documents:
            tf = tf_idf_computation.compute_tf(document)
            tf_idf_vector = {term: tf.get(term, 0) * self.idf.get(term, 0) for term in self.idf}
            tf_idf_vectors[doc_id] = tf_idf_vector
        return tf_idf_vectors