# main.py
from flask import Flask, jsonify, request
from flask_cors import cross_origin
from langchain.document_loaders import SeleniumURLLoader
from langchain.document_loaders.image import UnstructuredImageLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.document_loaders import YoutubeLoader
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from supabase import create_client, Client
import openai
import os
import requests


def download(url):
    get_response = requests.get(url, stream=True)
    file_name = url.split("/")[-1]
    with open(file_name, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return file_name

url: str = "https://gsaywynqkowtwhnyrehr.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdzYXl3eW5xa293dHdobnlyZWhyIiwicm9sZSI6ImFub24iLCJpYXQiOjE2Nzg3NTUzMDEsImV4cCI6MTk5NDMzMTMwMX0.AFuxpyRtVjW-qcGNxuWbai8zBo9H2EDGT3JlGZKpgzc"
supabase: Client = create_client(url, key)

app = Flask(__name__)

@app.route("/createEmbeddingForObject", methods=["POST"])
@cross_origin(supports_credentials=True)
def createEmbeddingForObjects():
    data = request.json
    url = data["url"]
    user = data["userID"]
    title = url.split("/")[-1]

    # download the file if its not a youtube video
    if "youtube" not in url:
        path = download(url)
    elif "youtube" in url:
        loader = YoutubeLoader.from_youtube_channel(
            url, add_video_info=True)
    elif path.endswith(".pdf"):
        loader = UnstructuredPDFLoader(path)
    elif path.endswith(".csv"):
        loader = CSVLoader(path)
    elif path.endswith(".jpg") or path.endswith(".png"):
        loader = UnstructuredImageLoader(path)
    elif path.endswith(".doc") or path.endswith(".docx"):
        loader = UnstructuredWordDocumentLoader(path)
    elif path.endswith(".ppt") or path.endswith(".pptx"):
        loader = UnstructuredPowerPointLoader(path)
    elif "http" in url:
        loader = SeleniumURLLoader([path])
    else:
        loader = UnstructuredFileLoader(path)
    data = loader.load()
    print(data)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(data)
    for chunk in docs:
        response = openai.Embedding.create(
            input=str(chunk.page_content),
            model="text-embedding-ada-002"
        )
        embeddings = response['data'][0]['embedding']
        data, _ = supabase.table('userdocuments').insert({
            "url": url,
            "userid": user,
            "body": chunk.page_content,
            "embedding": embeddings
        }).execute()
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
