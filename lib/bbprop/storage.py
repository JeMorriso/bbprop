from io import StringIO
from pathlib import Path
import json

import pandas as pd


class LocalStorage:
    def __init__(self, dir):
        self.dir = f"{str((Path() / Path(dir).resolve()))}"

    def dataframe_to_csv(self, df, path):
        df.to_csv(path, header=True, index=False)

    def csv_to_dataframe(self, path):
        return pd.read_csv(path)

    def load_json(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def generate_path(self, *args):
        clean_args = [a for a in args if a]
        return "/".join(clean_args)


class S3Storage:
    """Storage class interfacing with AWS S3 bucket.

    Root directory should not have slash at beginning.
    """

    def __init__(self, session, bucket, dir=""):
        # boto3 session from user or lambda role
        self.client = session.client("s3")
        self.resource = session.resource("s3")
        self.bucket = self.resource.Bucket(bucket)

        self.dir = dir

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

    def find_files(self, path):
        """Return paths of files with matching prefix."""
        objects = self.bucket.objects.filter(Prefix=path)
        keys = []
        for obj in objects:
            keys.append(obj.key)
        return set(keys)

    def find_file(self, path):
        """Return path of first file with matching prefix.

        Does not check for exact match. Ignores 'directories'. Note that 'directories'
        do not actually exist in S3.

        Example:
            path = 'foo/' ignores the 'foo' directory.
        """
        objects = list(self.find_files(path))
        objects = [o for o in objects if o[-1] != "/"]
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
        if not path:
            return {}
        obj = self.client.get_object(Bucket=self.bucket.name, Key=path)
        obj_str = obj["Body"].read().decode()
        return json.loads(obj_str)

    def generate_path(self, *args):
        clean_args = [a for a in args if a]
        return "/".join(clean_args)


class LeagueStorage:
    """Compose LocalStorage / S3Storage, add League specific storage configuration.

    Better to use composition here instead of trying to inherit from both.
    # TODO
    Currently will not work with LocalStorage due to required methods not implemented.

    Attributes:
        dir: League root directory.
        players_dir: Directory where players.json is found.
        bets_dir: Directory where archived bets csv files can be found.
        latest_dir: Directory holding the latest bets csv to be used by NextJS.
    """

    def __init__(self, store, dir):
        self.store = store
        self.dir = dir
        self.players_dir = "players"
        self.bets_dir = "bets"
        self.latest_dir = "latest"

    def players(self):
        path = self.store.generate_path(
            self.store.dir, self.dir, self.players_dir, "players.json"
        )
        return self.store.load_json(path)

    def latest(self):
        """Return the first file in the 'latest' directory."""
        path = self.store.generate_path(self.store.dir, self.dir, self.latest_dir)
        latest_file = self.store.find_file(path)
        bet_values = self.store.csv_to_dataframe(latest_file)
        bv_json = bet_values.to_json(orient="records")
        return bv_json
