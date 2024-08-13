import os
import json
from llama_index.embeddings.together import TogetherEmbedding # type: ignore
from llama_index.llms.together import TogetherLLM # type: ignore
from llama_index.core import GPTVectorStoreIndex,SimpleDirectoryReader, VectorStoreIndex, StorageContext # type: ignore
from llama_index.vector_stores import MilvusVectorStore # type: ignore
import openai
from milvus import default_server


# Load the API key from config.json file
with open("config.json", "r") as config_file:
    config = json.load(config_file)
    api_key = config.get("TOGETHER_API_KEY")

# Set OpenAI API key
openai.api_key = api_key

default_server.start()

vector_store = MilvusVectorStore(
    uri="./milvus_demo.db", dim=1536, overwrite=True
)
documents = SimpleDirectoryReader("output").load_data()

storage_context = StorageContext.from_defaults(vector_store = vector_store)
index = GPTVectorStoreIndex.form_documents(
    documents = documents,
    storage_context = storage_context
    )

query_engine = index.as_query_engine()

response = query_engine.query("summarize the following meeting notes into a structured summary. Include the meeting lead(if mentioned), key discussion points, action items, and decisions made. Format the summary with clear headings: dont give me ** in output and also dont start with heading meeting summary as heading i will add it manually myself")
print (response)