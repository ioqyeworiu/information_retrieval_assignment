import numpy

def cosin_sim(vecs1: dict[str, dict[str, float]], vecs2: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    if len(vecs1) == 0 or len(vecs2) == 0:
        raise ValueError("Vectors cannot be empty")
    
    if len(vecs1[list(vecs1.keys())[0]]) != len(vecs2[list(vecs2.keys())[0]]):
        raise ValueError("Vectors must be of the same dimension")

    sim_matrix = {}
    for doc_id1, vec1 in vecs1.items():
        sim_matrix[doc_id1] = {}
        for doc_id2, vec2 in vecs2.items():
            dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in set(vec1) | set(vec2))
            norm_vec1 = numpy.sqrt(sum(value ** 2 for value in vec1.values()))
            norm_vec2 = numpy.sqrt(sum(value ** 2 for value in vec2.values()))
            if norm_vec1 == 0 or norm_vec2 == 0:
                sim_matrix[doc_id1][doc_id2] = 0.0
            else:
                sim_matrix[doc_id1][doc_id2] = dot_product / (norm_vec1 * norm_vec2)       
    return sim_matrix                                                  