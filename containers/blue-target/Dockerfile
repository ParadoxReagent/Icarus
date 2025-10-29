FROM ubuntu:22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install necessary packages
RUN apt-get update && \
    apt-get install -y \
    apache2 \
    php \
    php-mysqli \
    php-gd \
    mysql-server \
    openssh-server \
    git \
    curl \
    wget \
    iptables \
    fail2ban \
    net-tools \
    vim \
    auditd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone and set up DVWA
WORKDIR /var/www/html
RUN git clone https://github.com/digininja/DVWA.git dvwa && \
    cd dvwa && \
    cp config/config.inc.php.dist config/config.inc.php

# Configure DVWA database settings
RUN sed -i "s/\$_DVWA\['db_password'\] = 'p@ssw0rd';/\$_DVWA['db_password'] = 'dvwa';/" /var/www/html/dvwa/config/config.inc.php && \
    sed -i "s/\$_DVWA\['recaptcha_public_key'\] = '';/\$_DVWA['recaptcha_public_key'] = 'disabled';/" /var/www/html/dvwa/config/config.inc.php && \
    sed -i "s/\$_DVWA\['recaptcha_private_key'\] = '';/\$_DVWA['recaptcha_private_key'] = 'disabled';/" /var/www/html/dvwa/config/config.inc.php

# Set permissions
RUN chown -R www-data:www-data /var/www/html/dvwa && \
    chmod -R 755 /var/www/html/dvwa

# Configure Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf && \
    a2enmod rewrite

# Set up SSH with weak password (for testing)
RUN mkdir -p /var/run/sshd && \
    echo 'root:password123' | chpasswd && \
    useradd -m -s /bin/bash admin && \
    echo 'admin:password123' | chpasswd && \
    usermod -aG sudo admin

# Allow password authentication for SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Create flag file
RUN echo "ICARUS{C0ngr4tul4t10ns_Y0u_H4v3_C0mpl3t3d_Th3_Ch4ll3ng3}" > /root/flag.txt && \
    chmod 600 /root/flag.txt

# Create startup script
RUN echo '#!/bin/bash\n\
service mysql start\n\
mysql -e "CREATE DATABASE IF NOT EXISTS dvwa;"\n\
mysql -e "CREATE USER IF NOT EXISTS '\''dvwa'\''@'\''localhost'\'' IDENTIFIED BY '\''dvwa'\'';"\n\
mysql -e "GRANT ALL PRIVILEGES ON dvwa.* TO '\''dvwa'\''@'\''localhost'\'';"\n\
mysql -e "FLUSH PRIVILEGES;"\n\
service apache2 start\n\
service ssh start\n\
service fail2ban start || true\n\
service auditd start || true\n\
tail -f /dev/null' > /start.sh && \
    chmod +x /start.sh

# Expose ports
EXPOSE 80 22

# Start services
CMD ["/start.sh"]
