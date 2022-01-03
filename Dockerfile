FROM python:3.8.1

ENV APP_HOME /src
WORKDIR $APP_HOME

COPY . /src
WORKDIR /src

RUN pip install -r requirements.txt

# ENTRYPOINT ["python app.py"]
# CMD [ "python", "./app.py" ]
ENTRYPOINT ["python", "app.py"]

