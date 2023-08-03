FROM python:3.11
COPY dist/* ~/src/querier/dist/
RUN pip3 install \~/src/querier/dist/querier*.tar.gz