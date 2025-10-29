FROM python:3.11-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    mongodb \
    curl \
    wget \
    net-tools \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python packages
RUN pip install --no-cache-dir \
    flask==3.0.0 \
    flask-cors==4.0.0 \
    pyjwt==2.8.0 \
    pymongo==4.6.1 \
    bcrypt==4.1.2 \
    python-dotenv==1.0.0

# Copy application files
COPY app.py /app/
COPY init_db.py /app/

# Create data directory for flag
RUN mkdir -p /app/data && \
    echo '{"flag": "ICARUS{AP1_H4ck3d_JWT_N0SQL_IDOR_Pwn3d}", "admin": "true", "secret_data": "classified"}' > /app/data/admin_flag.json && \
    chmod 600 /app/data/admin_flag.json

# Create startup script
RUN echo '#!/bin/bash\n\
mkdir -p /data/db\n\
mongod --fork --logpath /var/log/mongodb.log --dbpath /data/db\n\
sleep 3\n\
python /app/init_db.py\n\
python /app/app.py' > /start.sh && \
    chmod +x /start.sh

# Expose port
EXPOSE 5000

# Start services
CMD ["/start.sh"]
