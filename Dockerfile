FROM npodewitz/confd:latest


##############################
# Install dependencies
#COPY requirements.txt /usr/src/fints_downloader/
#RUN cd /usr/src/fints_downloader/
RUN apk -U upgrade
RUN apk add --update --no-cache python3 bash curl nginx supervisor py-pip
RUN rm /etc/nginx/conf.d/default.conf
RUN apk add --update --no-cache --virtual .build-deps python3-dev build-base \
      musl-dev
RUN pip3 install --upgrade pip wheel
COPY requirements.txt /usr/src/fints_downloader/
RUN cd /usr/src/fints_downloader/ && pip3 install --no-cache-dir -r requirements.txt
RUN apk del .build-deps


##############################
# Create directories and copy application
RUN mkdir -p /usr/src/fints_downloader/src/static && \
    mkdir -p /var/www/ && \
    ln -s /usr/src/fints_downloader/src /var/www/fints_downloader
    #ln -s /usr/src/fints_downloader/static /var/www/fints_downloader/static

COPY src/ /usr/src/fints_downloader/src/


##############################
# Migrate database and collect static files
RUN cd /usr/src/fints_downloader/src && \
      python3 manage.py migrate && \
      python3 manage.py collectstatic


##############################
# Create user
RUN addgroup -g 1000 fints && \
    adduser -u 1000 -G fints -h /usr/src/fints_downloader -D fints && \
    chown -Rh fints:fints /usr/src/fints_downloader && \
    echo "fints ALL=(ALL) NOPASSWD: /bin/chmod" >> /etc/sudoers


##############################
# Copy entrypoint, scripts and config
COPY scripts/* /usr/bin/
COPY etc/ /etc/



WORKDIR /usr/src/fints_downloader/src

EXPOSE 80 443

##############################
# Mount volumes
#VOLUME ["/usr/src/paperless/data", "/usr/src/paperless/media", "/consume", "/export"]
ENTRYPOINT ["/usr/bin/docker-entrypoint.sh"]

