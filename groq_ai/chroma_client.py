import chromadb

client = chromadb.Client()
collection = client.create_collection(name="my_collection")

collection.add(
    documents=["What is the capital of France?", "What is the capital of Germany?"],
    ids=["doc1", "doc2"])

all_docs = collection.get()

results = collection.query(
    query_texts=["Query is about Pizza"],
    n_results=2)
print("All documents in the collection:",results)





                         