# ECD Intensive Seminar

NOTE: This is an educational project created as part of the [Data Science Specialization @ ITBA](https://www.itba.edu.ar/postgrado/especializacion-en-ciencia-de-datos/) (webpage in spanish).

## Introduction

The goal of this project is to implement a implement a data science solution that includes modern data tools such as [Apache Airflow](https://airflow.apache.org/), [Apache Spark](https://spark.apache.org/) and [Apache Superset](https://superset.apache.org/).

## Running locally

Start by cloning this repo

`git clone git@github.com:facupalavecino/ecd-seminar.git`

Create an `.env` file based on `.env.template` and fill in your credentials.

### Docker

This project ships with a `docker-compose` file that will spin up services:

`docker-compose build && docker-compose up -d`

NOTE: Superset services are grouped in a [profile](https://docs.docker.com/compose/profiles/) and **do not** start up by default.
This is because we are lacking a Superset Docker image optimized for `arm64` architectures, and its performance is very very low in my machine (MBP M1 chip).

To spin up Superset:

`docker-compose --profile superset up -d`

### Development

Project's dependencies are managed by poetry:

Install poetry in your system if it is not already installed: [Poetry docs](https://python-poetry.org/docs/)

Install dependencies

`poetry install`
