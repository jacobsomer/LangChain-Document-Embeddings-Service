FROM --platform=linux/amd64  python:3.9

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
ENV PORT 8080
EXPOSE 8080

ENV OPENAI_API_KEY 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

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install --upgrade pip
# Install production dependencies.
RUN pip install -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app