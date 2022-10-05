FROM python:3.10-buster AS builder

RUN mkdir /src
WORKDIR /src

COPY ./ /src/
RUN pip install build
RUN python -m build

FROM python:3.10-alpine3.15

RUN mkdir /app
COPY --from=builder /src/dist/* ./
RUN pip install strichliste2influxdb-*.tar.gz

ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["strichliste2influxdb"]
CMD ["update"]