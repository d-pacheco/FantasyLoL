# Use an official Python runtime as a parent image
FROM python:3.10-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable for SQLite database path (modify as needed)
ENV DATABASE_URL="sqlite:///./fantasy-league-of-legends.db"

# Run main.py when the container launches
CMD ["python", "./main.py"]