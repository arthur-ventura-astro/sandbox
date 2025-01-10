FROM quay.io/astronomer/astro-runtime:12.4.0

USER root

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
# Note: if you are testing your pipeline locally you may need to adjust the zip version to your dev local environment
RUN unzip awscliv2.zip
RUN ./aws/install

USER astro
