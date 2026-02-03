# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# We include specific versions to avoid the smtpd/kafka issues we solved
RUN pip install --no-cache-dir \
    pandas \
    sqlalchemy \
    psycopg2-binary \
    kafka-python \
    scikit-learn \
    joblib \
    streamlit \
    plotly \
    streamlit-lottie \
    requests \
    aiosmtpd

# Copy the rest of the application code
COPY . .

# Default command (will be overridden by docker-compose)
CMD ["python", "src/detector.py"]
