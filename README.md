# Selenium-Docker-Scraper

This is a python project that uses selenium and docker to scrape data from the internet.

### Prerequisites

- Python 3.10
- Docker

### Installation

1. Clone the repository

```
git clone https://github.com/jacobsomer/selenium-docker-scraper.git
```

2. Install the python dependencies.

```
pip install -r requirements.txt
```

### Usage

1. Build the docker image

```
docker build -t selenium-docker-scraper .
```

2. Run the docker container

```
docker run -p 8080:8080 selenium-docker-scraper
```

3. Access the data by making a request to the given port

```
curl http://localhost:8080/test
```

### Deploy to Cloud Run

1. Create a container registry

```
gcloud beta auth configure-docker
```

2. Push the image to the container registry

```
docker tag selenium-docker-scraper gcr.io/<project-id>/selenium-docker-scraper
docker push gcr.io/<project-id>/selenium-docker-scraper
```

3. Deploy the container to Cloud Run

```
gcloud beta run deploy --image gcr.io/<project-id>/selenium-docker-scraper
```

4. Access the data by making a request to the given URL

```
curl http://<url>/test
```

### Note

This project is only meant for educational purposes. Do not use it for any malicious or illegal activities.
# chat-boba-extract
