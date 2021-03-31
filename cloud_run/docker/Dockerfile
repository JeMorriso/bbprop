# Credit: https://dev.to/googlecloud/using-headless-chrome-with-cloud-run-3fdp

# Use the official Python image.
FROM python:3.9

# Install manually all the missing libraries for Chrome.
RUN apt-get update
RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils libgbm1

# Install Chrome.
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

ADD bbprop bbprop
ADD app/app.py app/app.py
ADD app/middlewares.py app/middlewares.py
ADD app/docker_env.py app/docker_env.py

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 'app.app:app'