from abc import ABC, abstractmethod
from io import StringIO
from pathlib import Path
import re
import json

import pandas as pd


class Storage(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def dataframe_to_csv(self, df, path):
        pass

    @abstractmethod
    def csv_to_dataframe(self, path):
        pass


class LocalStorage(Storage):
    def __init__(self, dir):
        # add trailing slash to make path compatible with local or s3
        self.dir = f"{str((Path() / Path(dir).resolve()))}/"
        self.game_log_dir = f"{self.dir}game-logs"
        self.bets_dir = f"{self.dir}bets"

    def root_dir(self):
        return self.dir

    def dataframe_to_csv(self, df, path):
        df.to_csv(path, header=True, index=False)

    def csv_to_dataframe(self, path):
        return pd.read_csv(path)

    def player_names(self):
        csvs = [p for p in Path(self.game_log_dir).iterdir() if p.is_file()]
        return [csv.name.replace(".csv", "") for csv in csvs]

    def load_json(self, path):
        with open(path, "r") as f:
            return json.load(f)


class S3Storage(Storage):
    def __init__(self, session, bucket):
        # boto3 session from user or lambda role
        self.client = session.client("s3")
        self.resource = session.resource("s3")
        self.bucket = self.resource.Bucket(bucket)
        self.game_log_dir = "game-logs"
        self.bets_dir = "bets"

    def root_dir(self):
        return ""

    def dataframe_to_csv(self, df, path):
        # don't export to file, return csv string
        csv_str = df.to_csv(header=True, index=False)
        # put_object method requires byte stream, not string
        csv_stream = bytes(csv_str.encode("UTF-8"))

        self.client.put_object(Bucket=self.bucket.name, Key=path, Body=csv_stream)

    def csv_to_dataframe(self, path):
        obj = self.client.get_object(Bucket=self.bucket.name, Key=path)
        csv_str = obj["Body"].read().decode("UTF-8")

        return pd.read_csv(StringIO(csv_str))

    def player_names(self):
        prefix = f"{self.game_log_dir}/"
        objects = self.client.list_objects_v2(Bucket=self.bucket.name, Prefix=prefix)
        keys = [f["Key"] for f in objects["Contents"]]
        # Remove the matching directory, Prefix doesn't support regex.
        paths = [k for k in keys if re.match(fr"{prefix}.+", k)]
        files = [re.sub(fr"^{prefix}", "", f) for f in paths]
        players = [re.sub(r"\.csv$", "", f) for f in files]
        return players

    def find_files(self, path):
        """Return paths of files with matching prefix."""
        objects = self.bucket.objects.filter(Prefix=path)
        keys = []
        for obj in objects:
            keys.append(obj.key)
        return set(keys)

    def find_file(self, path):
        """Return path of first file with matching prefix.

        Does not check for exact match.
        """
        objects = self.find_files(path)
        if objects:
            return objects.pop()
        else:
            return ""

    def move_file(self, source, dest):
        """Move file within bucket."""
        source_dict = {"Bucket": self.bucket.name, "Key": source}
        source_obj = self.resource.Object(self.bucket.name, source)
        self.bucket.copy(source_dict, dest)

        source_obj.delete()

    def load_json(self, path):
        obj = self.client.get_object(Bucket=self.bucket.name, Key=path)
        obj_str = obj["Body"].read().decode()
        return json.loads(obj_str)


class BallDontLieStorage:
    """Compose LocalStorage / S3Storage, add BallDontLie specific configuration."""

    def __init__(self, store):
        self.store = store
        self.dir = "players"

    def bets_dir(self):
        """Return path to bets directory."""
        return self.store.bets_dir

    def players(self):
        path = f"{self.store.root_dir()}{self.dir}/balldontlie_players.json"
        return self.store.load_json(path)
