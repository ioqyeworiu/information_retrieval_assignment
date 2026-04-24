from langchain.text_splitter import RecursiveCharacterTextSplitter
from glob import glob
import json
from tqdm import tqdm
import os

def split_txt(input_folder, output_folder, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    document_paths = glob(f"{input_folder}/*.txt")
    for document_path in tqdm(document_paths, desc="Splitting documents"):
        with open(document_path, "r", encoding="utf-8") as f:   
            text = f.read()
            chunks = text_splitter.split_text(text)
            for i, chunk in enumerate(chunks):
                output_path = f"{output_folder}/{document_path.split('/')[-1].split('.')[0]}_chunk_{i+1}.txt"
                output_path = output_path.replace("\\", "/")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as out_f:
                    out_f.write(chunk)
        
def split_jsonl(input_folder, output_folder, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    document_paths = glob(f"{input_folder}/*.jsonl")
    for document_path in tqdm(document_paths, desc="Splitting documents"):
        with open(document_path, "r", encoding="utf-8") as f:   
            lines = f.readlines()
            for j, line in enumerate(lines):
                data = json.loads(line)["page_content"]
                chunks = text_splitter.split_text(data)
                for i, chunk in enumerate(chunks):
                    output_path = f"{output_folder}/{document_path.split('/')[-1].split('.')[0]}_line_{j+1}_chunk_{i+1}.txt"
                    output_path = output_path.replace("\\", "/")
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, "w", encoding="utf-8") as out_f:
                        out_f.write(chunk)

split_txt("E:/UNIVERSITY_SUBJECTS/projects/Intelligent-Fitness-Recommendation-Coaching-System/data/Knowedge_base_RAG/processed/blogs", "E:/UNIVERSITY_SUBJECTS/projects/Intelligent-Fitness-Recommendation-Coaching-System/data/Knowedge_base_RAG/chunks")
split_txt("E:/UNIVERSITY_SUBJECTS/projects/Intelligent-Fitness-Recommendation-Coaching-System/data/Knowedge_base_RAG/processed/books", "E:/UNIVERSITY_SUBJECTS/projects/Intelligent-Fitness-Recommendation-Coaching-System/data/Knowedge_base_RAG/chunks")
split_jsonl("E:/UNIVERSITY_SUBJECTS/projects/Intelligent-Fitness-Recommendation-Coaching-System/data/Knowedge_base_RAG/processed/pubmed", "E:/UNIVERSITY_SUBJECTS/projects/Intelligent-Fitness-Recommendation-Coaching-System/data/Knowedge_base_RAG/chunks")
