# Use the official slim Python 3.9 image from Docker Hub
FROM python:3.9-slim

# Install dependencies needed to perform a git clone (git is not included in slim)
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean

# Set the working directory
WORKDIR /app

# Clone the git repository as the root user
RUN git clone -b updated_video_stream https://github.com/projectaws741/video_project_AWS_python.git .

# Create a user to run the application after cloning the repository
RUN useradd -m pyapp

# Change ownership of the /app directory to the new user
RUN chown -R pyapp:pyapp /app

# Switch to the new user
USER pyapp

# If your requirements.txt is in a subdirectory, adjust the path accordingly
# Install python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose port 5000
EXPOSE 5000

# Define the command to run your application
# Replace this with your actual command
CMD ["python3", "/app/app.py"]
