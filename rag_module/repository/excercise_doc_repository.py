from rag_module.util.database import Session_local
from rag_module.model.excercise_doc import ExerciseDoc


class ExerciseDocRepository:
    def __init__(self):
        self.db = Session_local()

    def get_exercise_doc_by_id(self, exercise_doc_id: int) -> ExerciseDoc:
        return self.db.query(ExerciseDoc).filter(ExerciseDoc.id == exercise_doc_id).first()