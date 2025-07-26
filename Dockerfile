FROM python:3.9-slim

WORKDIR /app

# Environment variable to prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1

# Environment variable to buffer stdout and stderr
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Default port
EXPOSE 5000

# Run the application
CMD ["flask", "run"]
