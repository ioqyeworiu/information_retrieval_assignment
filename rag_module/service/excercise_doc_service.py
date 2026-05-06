from rag_module.repository.excercise_doc_repository import ExerciseDocRepository
from rag_module.repository.user_repository import UserRepository
from fastapi import Depends, Request
from rag_module.util.query import Query
from similarity_module.cosin_sim import cosin_sim

class ExerciseDocService:
    def __init__(self, request: Request, exercise_doc_repository: ExerciseDocRepository = Depends(), user_repository: UserRepository = Depends()):
        self.exercise_doc_repository = exercise_doc_repository
        self.user_repository = user_repository
        self.vector_store = request.app.state.vector_store_1
        self.tf_idf_vectorizer = request.app.state.tf_idf_vectorizer
        self.bm25 = request.app.state.bm25
        self.documents = request.app.state.documents

    def get_exercise_doc_by_id(self, exercise_doc_id: int):
        return self.exercise_doc_repository.get_exercise_doc_by_id(exercise_doc_id)
    
    def get_exercise_doc(self, credentials: int, query_params: Query, query: str):
        user = self.user_repository.get_user_by_id(credentials)
        # self.vector_store.search_kwargs = {"n": query_n}
        if not query:
            query = f"""
                {user.goal}
            """
        if query_params.similarity_type == "embedding":
            results = self.vector_store.similarity_search(query, k=query_params.query_n)
            return results
        if query_params.similarity_type == "bm25":
            scores = self.bm25.scores(query)
            sorted_scores = sorted([(key, scores[key]) for key in scores.keys()], key=lambda x: x[1], reverse=True)
            results = self.vector_store.get_by_ids([id for id, score in sorted_scores[:query_params.query_n]])
            return results
        if query_params.similarity_type == "tf-idf":
            query_vec = self.tf_idf_vectorizer.transform([("query", query)])
            doc_vecs = self.tf_idf_vectorizer.transform(self.documents)
            scores = cosin_sim(query_vec, doc_vecs)["query"]
            sorted_scores = sorted([(key, scores[key]) for key in scores.keys()], key=lambda x: x[1], reverse=True)
            results = self.vector_store.get_by_ids([id for id, score in sorted_scores[:query_params.query_n]])
            return results