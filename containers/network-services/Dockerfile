FROM ubuntu:20.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install multiple vulnerable services
RUN apt-get update && \
    apt-get install -y \
    vsftpd \
    openssh-server \
    samba \
    telnetd \
    xinetd \
    nfs-kernel-server \
    net-tools \
    iptables \
    fail2ban \
    vim \
    curl \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure FTP (anonymous access enabled - vulnerability)
RUN echo "anonymous_enable=YES" >> /etc/vsftpd.conf && \
    echo "anon_upload_enable=YES" >> /etc/vsftpd.conf && \
    echo "anon_mkdir_write_enable=YES" >> /etc/vsftpd.conf && \
    echo "write_enable=YES" >> /etc/vsftpd.conf && \
    mkdir -p /var/ftp/pub && \
    chmod 777 /var/ftp/pub

# Configure SSH with weak passwords
RUN mkdir -p /var/run/sshd && \
    echo 'root:toor' | chpasswd && \
    useradd -m -s /bin/bash ftpuser && \
    echo 'ftpuser:ftp123' | chpasswd && \
    useradd -m -s /bin/bash smbuser && \
    echo 'smbuser:smb123' | chpasswd

# Allow password authentication for SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Configure Samba with weak security
RUN echo "[share]" >> /etc/samba/smb.conf && \
    echo "   path = /srv/samba/share" >> /etc/samba/smb.conf && \
    echo "   browseable = yes" >> /etc/samba/smb.conf && \
    echo "   read only = no" >> /etc/samba/smb.conf && \
    echo "   guest ok = yes" >> /etc/samba/smb.conf && \
    echo "   create mask = 0777" >> /etc/samba/smb.conf && \
    mkdir -p /srv/samba/share && \
    chmod 777 /srv/samba/share && \
    echo "smbuser:smb123" | smbpasswd -a smbuser -s

# Configure Telnet
RUN echo "telnet stream tcp nowait telnetd /usr/sbin/tcpd /usr/sbin/in.telnetd" > /etc/xinetd.d/telnet

# Create secrets and flag
RUN mkdir -p /opt/secrets && \
    echo "ICARUS{N3tw0rk_S3rv1c3s_Pwn3d_L1k3_A_B0ss}" > /opt/secrets/flag.txt && \
    chmod 600 /opt/secrets/flag.txt && \
    echo "database_password=super_secret_123" > /opt/secrets/config.txt && \
    chmod 644 /opt/secrets/config.txt

# Create vulnerable cron job directory (for persistence)
RUN mkdir -p /var/spool/cron/crontabs && \
    chmod 1730 /var/spool/cron/crontabs

# Add some decoy files in FTP
RUN echo "Welcome to the FTP server" > /var/ftp/pub/readme.txt && \
    echo "backup_schedule=daily" > /var/ftp/pub/config.txt

# Create startup script
RUN echo '#!/bin/bash\n\
service vsftpd start\n\
service ssh start\n\
service smbd start\n\
service nmbd start\n\
service xinetd start\n\
service fail2ban start || true\n\
echo "All services started"\n\
tail -f /dev/null' > /start.sh && \
    chmod +x /start.sh

# Expose ports
EXPOSE 21 22 23 139 445 2049

# Start services
CMD ["/start.sh"]
