import os

import boto3
import pytest
from dotenv import load_dotenv

from chalicelib.storage import S3Storage, LeagueStorage

load_dotenv()


@pytest.fixture
def s3storage():
    """S3Storage configured with tests/ directory as its root dir."""
    return S3Storage(
        session=boto3.session.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        ),
        bucket=os.getenv("S3_BUCKET"),
        dir="tests",
    )


@pytest.fixture
def s3storage_prod():
    return S3Storage(
        session=boto3.session.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        ),
        bucket=os.getenv("S3_BUCKET"),
        dir="",
    )


@pytest.fixture
def leaguestorage_NBA(s3storage_prod):
    return LeagueStorage(s3storage_prod, "NBA")


@pytest.fixture
def leaguestorage_NBA_test(s3storage):
    """Use tests directory on S3 instead of NBA folder for some tests."""
    return LeagueStorage(s3storage, "NBA")


@pytest.fixture
def nba_latest():
    return "2021-02-26T00:04:23.csv"
