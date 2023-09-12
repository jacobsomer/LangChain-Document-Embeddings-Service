# LangChain Document Embedding API

This is a Flask API for extracting text from PDFs, PowerPoints, XL Spreadsheets, Youtube Channels, and more. 

## Prerequisites

- Docker
- Docker Compose

## Usage

1. Clone the repository and navigate to the root directory.
2. Run the following command to start the API:

```
docker-compose up
```

This will start the API on http://localhost:5000.

3. To extract text from a PDF, make a `POST` request to `http://localhost:5000/getTextForPDF` with the following JSON data:

```
{
"url": "https://example.com/path/to/pdf"
}
```

This will return the extracted text from the PDF as a JSON response.

4. To extract text from an HTML page, make a `POST` request to `http://localhost:5000/getTextForURL` with the following JSON data:

```
{
"url": "https://example.com"
}
```

This will return the extracted text and title from the HTML page as a JSON response.

## Configuration

The following environment variables can be set to configure the API:

- `PORT`: The port on which the API should listen. Default is `5000`.

## Dependencies

The API uses the following dependencies:

- Flask==2.2.2
- Flask-Cors==3.0.10
- gunicorn==20.1.0
- selenium==4.7.2
- PyPDF2==3.0.1
- timeout-decorator==0.5.0
- beautifulsoup4==4.11.2
