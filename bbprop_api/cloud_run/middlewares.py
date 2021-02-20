import pandas as pd
import boto3

from bbprop.sportapi import NBA
from bbprop.storage import S3Storage
from docker_env import S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def s3storage():
    return S3Storage(
        # session=boto3.session.Session(profile_name="default"),
        session=boto3.session.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        ),
        bucket=S3_BUCKET,
    )


def get_nba_game_logs(players, store):
    """Given a list of players, get their game logs from store.

    If game log doesn't exist for player, retrieve and store it.

    Returns:
        Tuple containing game log and its source, either 'Store' or 'API'.
    """

    def try_get_game_log(player):
        # TODO: handle NoSuchKey from boto3
        p_df = store.csv_to_dataframe(f"{store.game_log_dir}/{player}")
        if not p_df:
            try:
                player_obj = nba.player_by_name(player)
                return nba.season_game_log(player_obj["id"], "2020-21"), "API"

            except KeyError:
                return pd.DataFrame(), ""
        else:
            return p_df, "Store"

    nba = NBA()
    game_logs = {}

    for p in players:
        p_df, source = try_get_game_log(p)
        if p_df:
            game_logs[p] = p_df
            if source == "API":
                store.dataframe_to_csv(p_df, f"{store.game_log_dir}/{p}.csv")


def write_nba_game_logs(store):
    """Overwrite all game logs.

    Gets list of players from the data store, and then retrieves all game logs, writing
    them back to the data store.
    """

    nba = NBA()
    ps = store.player_names()
    game_logs = {}
    for p in ps:
        game_log = nba.season_game_log_by_name(p, "2020-21")

        if not game_log.empty:
            game_logs[p] = game_log
    for k, v in game_logs.items():
        store.dataframe_to_csv(v, f"{store.game_log_dir}/{k}.csv")
