FROM mcr.microsoft.com/devcontainers/python:0-3.10

# TODO: Implement debian apt sources in nexus to allow downloading of packages here.
# For now, the VM inside the TRE has the ODBC drivers we need installed, and the 
# pip packages can be downloaded via nexus, so there's no 'need' for this dev container
# inside the TRE. Then you can uncomment the lines below.

# Install ODBC Driver
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl -fsSL https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
RUN ["/bin/bash", "-c", "source ~/.bashrc"]
RUN apt-get install -y unixodbc-dev

# Install AZ CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
