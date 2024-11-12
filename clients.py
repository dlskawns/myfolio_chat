import boto3
import os
from langchain.vectorstores import Chroma
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
import streamlit as st

vdb_instance = None


class vectordb:
    def __init__(self):
        self.bucket_name = "chatbot-myfolio-changsa"
        self.folder_path = "chroma_db"
        self.local_path = "/tmp/chroma_db"
        self.s3 = boto3.client('s3')
        self.download_s3_folder(self.bucket_name, self.folder_path, self.local_path)
        self.embedding = self.embedding_model()
        self.hugging_vectorstore = Chroma(persist_directory=self.local_path , embedding_function=self.embedding)
    
    # S3 폴더의 모든 파일을 로컬 경로로 다운로드하는 함수
    def download_s3_folder(self, bucket_name, folder_path, local_path):
        print('vectorDB 다운로드중')
        os.makedirs(local_path, exist_ok=True)
        for obj in self.s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)['Contents']:
            # S3 키에서 파일 이름 추출 후 로컬에 저장
            print('obj', obj)
            file_key = obj['Key']
            if file_key.endswith('/'):
                continue  # 폴더 경로는 건너뜁니다.
            local_file_path = os.path.join(local_path, os.path.basename(file_key))
            self.s3.download_file(bucket_name, file_key, local_file_path)
 
    def embedding_model(self):
        print('임베딩모델 다운로드중')
        # Embedding 모델 불러오기 - 개별 환경에 맞는 device로 설정
        model_name = "BAAI/bge-m3"
        model_kwargs = {
            # "device": "cuda"
            "device": "mps"
            # "device": "cpu"
        }
        encode_kwargs = {"normalize_embeddings": True}
        hugging_embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,)
        return hugging_embeddings
def get_vectordb():
    global vdb_instance
    if vdb_instance is None:
        vdb_instance = vectordb()  # 인스턴스를 한 번만 생성
    return vdb_instance