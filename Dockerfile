FROM debian:stretch

# Install Python-related packages
RUN apt-get update -y && apt-get -y install python3.5 python3-pip curl
RUN pip3 install flask sqlalchemy==1.1.13 psycopg2==2.7.1 pandas requests pyyaml
RUN pip3 install tornado

# Create folders
RUN mkdir -p /data
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

# Launch app
CMD [ "python3", "-u", "./launch_server.py" ]
