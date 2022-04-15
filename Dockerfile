FROM python:3.10
# Installing dependencies
RUN apt-get update && \
    apt-get install --yes curl wget unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
# Install Google Chrome
RUN apt-get update && \
    wget --quiet https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    (dpkg --install google-chrome-stable_current_amd64.deb || DEBIAN_FRONTEND=noninteractive apt-get --fix-broken --yes install) && \
    rm google-chrome-stable_current_amd64.deb && \
    sed -i 's|HERE/chrome"|HERE/chrome" --disable-setuid-sandbox --no-sandbox|g' "/opt/google/chrome/google-chrome" && \
    google-chrome --version && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/*
# Install Chromedriver
RUN CHROMEDRIVER_RELEASE=$(curl http://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    echo "Chromedriver latest version: $CHROMEDRIVER_RELEASE" && \
    wget --quiet "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_RELEASE/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip && \
    rm -rf chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    chromedriver --version


COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]