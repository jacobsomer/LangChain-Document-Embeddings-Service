from flask import Flask, jsonify, request
from flask_cors import cross_origin
from langchain.document_loaders import SeleniumURLLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from supabase import create_client, Client
import openai
import os
import requests
from pytube import extract
from youtube import scrape_youtube_info
from youtube_transcript_api import YouTubeTranscriptApi
from newspaper import fulltext, Article

supported_file_extensions = ['.txt', '.csv', '.pdf', '.doc', '.docx', '.ppt', '.pptx']

def url_to_filename(url, ext):
    return url.split(ext)[0].split("/")[-1] + ext

def urlContainsExtension(url):
    for ext in supported_file_extensions:
        if ext in url:
            return ext
    return "None"

# currently supports youtube wikipedia
def extract(url):
    ext = urlContainsExtension(url)
    if ext != "None":
        get_response = requests.get(url, stream=True)
        path = url_to_filename(url, ext)
        with open(path, 'wb') as f:
            for chunk in get_response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return path, path
    if "youtube" in url or "youtu" in url:
        video_id = extract.video_id(url)
        res = YouTubeTranscriptApi.get_transcript(video_id)
        name = scrape_youtube_info(url)["title"]
        transcriptString = ""
        for i in res:
            if i["text"] is not None:
                transcriptString += i["text"]
        with open("transcript.txt", "w") as f:
            f.write(transcriptString)
        return  "transcript.txt", name
    elif "wikipedia" in url:
        html = requests.get(url).text
        text = fulltext(html)
        with open("wiki.txt", "w") as f:
            f.write(text)
        return "wiki.txt", "NoName"
    else:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text
        if len(text) < 100:
            return "None", "None"
        with open("article.txt", "w") as f:
            f.write(text)
        return "article.txt", article.title

url: str = "https://gsaywynqkowtwhnyrehr.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdzYXl3eW5xa293dHdobnlyZWhyIiwicm9sZSI6ImFub24iLCJpYXQiOjE2Nzg3NTUzMDEsImV4cCI6MTk5NDMzMTMwMX0.AFuxpyRtVjW-qcGNxuWbai8zBo9H2EDGT3JlGZKpgzc"
supabase: Client = create_client(url, key)

app = Flask(__name__)

def deleteFile(path):
    try:
        os.remove(path)
    except Exception as e:
        app.logger.error("Error deleting file: " + str(e))
    
def getEmbeddingsForData(data):
    chunkSizes = [4000, 2000, 1000]
    for chunkSize in chunkSizes:
        try:
            embeddingRet = []
            text_splitter = CharacterTextSplitter(separator = "\n\n",
                chunk_size = chunkSize,
                chunk_overlap  = 200,
                length_function = len)
            docs = text_splitter.split_documents(data)
            for chunk in docs: 
                chunkString = str(chunk.page_content)
                response = openai.Embedding.create(
                    input=chunkString,
                    model="text-embedding-ada-002"
                )
                embeddings = response['data'][0]['embedding']
                embeddingRet.append([embeddings, chunkString])
            return embeddingRet
        except openai.error.InvalidRequestError as e:
            app.logger.error("Chunk size too large, trying with a smaller chunk size")
        except Exception as e:
            app.logger.error("Error: " + str(e))
    return []

@app.route("/createEmbeddingForObject", methods=["POST"])
@cross_origin(supports_credentials=True)
def createEmbeddingForObjects():
    data = request.json
    url = data["url"]
    docId = data["docId"]
    # check if the url is already in the database
    data, _ = supabase.table('userdocuments').select("docId").eq("url", url).execute()
    if len(data[1]) > 0:
        app.logger.info(str(data))
        return jsonify({"docId": str(data[1][0]["docId"])}), 200
    # download the file if its not a youtube video
    path, name = extract(url)
    if path == "None":
        return jsonify({"error": "Invalid url"}), 400
    try:
        if path.endswith(".pdf"):
            loader = UnstructuredPDFLoader(path)
        elif path.endswith(".csv"):
            loader = CSVLoader(path)
        elif path.endswith(".doc") or path.endswith(".docx"):
            loader = UnstructuredWordDocumentLoader(path)
        elif path.endswith(".ppt") or path.endswith(".pptx"):
            loader = UnstructuredPowerPointLoader(path)
        elif list(filter(path.endswith, supported_file_extensions)) != []:
            loader = UnstructuredFileLoader(path)
        else:
            deleteFile(path)
            return jsonify({"error": "Invalid file type"}), 400
        data = loader.load()
        if len(data) == 0:
            deleteFile(path)
            return jsonify({"error": "No data found"}), 400
        elif data[0].page_content == "":
            deleteFile(path)
            return jsonify({"error": "No data found"}), 400
        embeddings = getEmbeddingsForData(data)
        for e in embeddings:
            if name == "NoName":
                # use openai to get the name of the document from the first chunk of text
                response = openai.Completion.create(
                    engine="davinci",
                    prompt=e[1]+"\n\n URL:"+ url+"\n\n Name of Document or Webpage:",
                    temperature=0.5,
                    max_tokens=5,
                    top_p=1,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )
                name = str(response["choices"][0]["text"])
            embedding, body = e
            data, _ = supabase.table('userdocuments').insert({
                "url": url,
                "docId": docId,
                "body": body,
                "embedding": embedding,
                "name": name
            }).execute()
        if "http" not in path:
            deleteFile(path)
        return jsonify({"docId": docId}), 200
    except Exception as e:
        app.logger.error("Error: " + str(e))
        deleteFile(path)
        return jsonify({"error": "Error"}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))