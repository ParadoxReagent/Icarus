FROM kalilinux/kali-rolling

# Update and install essential tools for MVP
RUN apt-get update && \
    apt-get install -y \
    nmap \
    curl \
    wget \
    netcat-traditional \
    iputils-ping \
    dnsutils \
    net-tools \
    nikto \
    dirb \
    sqlmap \
    hydra \
    metasploit-framework \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /root

# Initialize metasploit database (optional, can be done at runtime)
RUN service postgresql start && \
    msfdb init || true && \
    service postgresql stop

# Keep container running
CMD ["tail", "-f", "/dev/null"]
