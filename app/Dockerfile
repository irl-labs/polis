FROM python:3.8

# set a directory for the app
WORKDIR /usr/src/app

# copy all the files to the container
COPY . .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt



# tell the port number the container should expose
EXPOSE 5000

# run the command

#ENTRYPOINT exec gunicorn --bind :5000 --workers 1 polis:server

CMD ["gunicorn"  , "-b", "0.0.0.0:5000", "polis:server"]

#CMD ["python", "./polis.py"]
