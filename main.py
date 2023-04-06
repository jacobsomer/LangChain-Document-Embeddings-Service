# main.py
from flask import Flask, jsonify, request
from flask_cors import cross_origin
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import timeout_decorator
from langchain.document_loaders import SeleniumURLLoader
from langchain.document_loaders.image import UnstructuredImageLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import UnstructuredURLLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.document_loaders import YoutubeLoader
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


app = Flask(__name__)


@app.route("/createEmbeddingForText", methods=["POST"])
@cross_origin(supports_credentials=True)
def createEmbeddingForText():
    data = request.json
    url = data["url"]
    text = data["text"]
    user = data["userID"]
    title = url.split("/")[-1]
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embeddings = response['data'][0]['embedding']
    data, _ = supabase.table('userdocuments').insert({
        "url": url,
        "title": title,
        "userID": user,
        "embeddings": embeddings
    }).execute()
    return jsonify(data)


@app.route("/createEmbeddingForObject", methods=["POST"])
@cross_origin(supports_credentials=True)
def createEmbeddingForObjects():
    data = request.json
    url = data["url"]
    user = data["userID"]
    title = url.split("/")[-1]
    if url.endswith(".pdf"):
        loader = UnstructuredPDFLoader(url)
    elif url.endswith(".csv"):
        loader = CSVLoader(url)
    elif url.endswith(".jpg") or url.endswith(".png"):
        loader = UnstructuredImageLoader(url)
    elif url.endswith(".doc") or url.endswith(".docx"):
        loader = UnstructuredWordDocumentLoader(url)
    elif url.endswith(".ppt") or url.endswith(".pptx"):
        loader = UnstructuredPowerPointLoader(url)
    elif "youtube" in url:
        # !pip install youtube-transcript-api
        # ! pip install pytube
        loader = YoutubeLoader.from_youtube_url(
            "https://www.youtube.com/watch?v=QsYGlZkevEg", add_video_info=True)
    else:
        loader = SeleniumURLLoader([url])
    data = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(data)
    for chunk in docs:
        response = openai.Embedding.create(
            input="Your text string goes here",
            model="text-embedding-ada-002"
        )
        embeddings = response['data'][0]['embedding']
        data, _ = supabase.table('userdocuments').insert({
            "url": url,
            "title": title,
            "userID": user,
            "embeddings": embeddings
        }).execute()
    return jsonify(data)
