# FROM python:3.10-slim

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Set the working directory inside the container
# WORKDIR /code

# # Copy the requirements file first for caching dependencies
# COPY requirements.txt /code/

# # Install dependencies
# RUN pip install --upgrade pip && pip install -r requirements.txt

# # Copy the entire project into the container
# COPY . /code/

# # Expose the port the app will run on
# EXPOSE 8000

# # Run the Django development server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Dockerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "snipbox.wsgi:application", "--bind", "0.0.0.0:8000"]

