# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app


# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Expose port 80
EXPOSE 80

# Define environment variable
ENV NAME World

# Specify the command to run on container start
ENTRYPOINT ["python", "app.py"]

