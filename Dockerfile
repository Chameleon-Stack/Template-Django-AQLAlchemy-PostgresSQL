FROM python
WORKDIR /app
COPY . .
RUN pip install pipenv
RUN pipenv requirements > requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8080
CMD [ "python", "manage.py", "runserver" ]
