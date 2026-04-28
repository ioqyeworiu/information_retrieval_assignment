from pydantic import BaseModel, Field


class InvertedIndex(BaseModel):
    vocab: dict[str, list[int]] = Field(default=dict())

    @classmethod
    def build(cls, documents: list[tuple[str, str]]) -> dict[str, list[int]]:
        self = cls()
        word_docID = []
        # step 1: map
        for doc in documents:
            doc_id, text = doc
            for word in text.split():
                word_docID.append((word, doc_id))

        # step 2: reduce
        word_docID = sorted(word_docID, key=lambda x: (x[0], x[1]))
        for word, doc_id in word_docID:
            if word not in self.vocab.keys():
                self.vocab[word] = []
            self.vocab[word].append(doc_id)
        return self.vocab