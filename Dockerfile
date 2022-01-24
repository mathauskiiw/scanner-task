# Use the official Python image from the Docker Hub
FROM python:3.10.1

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Update & upgrade
RUN apt update && apt upgrade -y

# Installs chrome
RUN apt install chromium -y

# Create app user in the app group
RUN useradd --user-group --create-home --no-log-init --shell /bin/bash cr4wler

ENV APP_HOME=/home/cr4wler/scanner_task

# Change the workdir
WORKDIR $APP_HOME

# Copy the code.
COPY . $APP_HOME

RUN chmod +x ./entry.sh

RUN chown -R cr4wler:cr4wler $APP_HOME

USER cr4wler:cr4wler

# RUN echo "export PATH=/new/path:${PATH}" >> ~/.bashrc
# RUN bash -c "source ~/.bashrc"
ENV PATH "$PATH:/home/cr4wler/.local/bin"
RUN echo $PATH

# Upgrade pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# Install poetry
RUN /usr/local/bin/python -m pip install poetry

# Install all dependencies
RUN poetry install


ENTRYPOINT ["/home/cr4wler/scanner_task/entry.sh"]