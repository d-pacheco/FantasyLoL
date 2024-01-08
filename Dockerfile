FROM python:3.10-alpine

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./fantasylol /app/fantasylol
COPY ./main.py /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable for SQLite database path (modify as needed)
ENV DATABASE_URL="sqlite:///./database/fantasy-league-of-legends.db"

# Run main.py when the container launches
CMD ["python", "./main.py"]