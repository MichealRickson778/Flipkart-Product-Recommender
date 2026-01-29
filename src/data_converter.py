import pandas as pd
from langchain_core.documents import Document

class DataConverter:
    def __init__(self, file_path:str):
        self.file_path = file_path
        
    def convert(self) -> dict:
        df = pd.read_csv(self.file_path)[["product_title","review"]]

        df = (
            df.rename(columns=lambda x : x.strip().lower())
            .dropna(subset=["product_title","review"])  
              )

        docs =[
            Document(
                page_content=str(review), metadata={"product_name":str(tittle)}
                )
                for tittle,review in zip(df["product_title"],df["review"])
        ]

        return docs