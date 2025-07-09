import pandas as pd
import chromadb
import uuid

class Portfolio:
    def __init__(self, file_path="resource/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        print("Portfolio Data Loaded:", self.data.head())
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if not self.collection.count():
            print("Collection empty, loading portfolio...")
            for _, row in self.data.iterrows():
                print("Adding:", row["Techstack"], row["Links"])
                self.collection.add(
                    documents=[str(row["Techstack"])],
                    metadatas=[{"links": str(row["Links"])}],
                    ids=[str(uuid.uuid4())]
                )
            print("Portfolio loaded. Collection count:", self.collection.count())
        else:
            print("Collection already loaded. Count:", self.collection.count())

    def query_links(self, skills):
        return self.collection.query(query_texts=skills, n_results=2).get('metadatas', [])