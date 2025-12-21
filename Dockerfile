FROM python:3.10-slim-bullseye  
# Explicitly uses Debian 11 (Bullseye)

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl -sSL https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]