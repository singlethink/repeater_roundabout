import re
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

logs_dir = Path("logs")
logs_files = logs_dir.glob("*.csv")


def signal_report_to_readability(report: str) -> Optional[int]:
    """
    A rough interpretation of signal reports into numerical values.

    For circuit merit reports, we just return the number of the report.
    For RST reports, we return the Readability component.

    Parameters
    ----------
    report : str
        A user's signal report, such as "CM4" or "59".

    Returns
    -------
    Optional[int]
        The readability of a signal report, or None if it couldn't be interpreted.
    """

    # Will match CM4, CM5+, CM3.5, CM4.5+
    is_cm = re.fullmatch(
        r"""
            ^
            CM  # starts with "CM"
            ([1-5])  # followed by a number from 1 to 5 -- this is what we return
            \+?  # optionally followed by a plus sign ( CM5+ )
            (?:.\d)?  # optionally followed by a decimal and a number ( CM4.5 )
            $
        """,
        report,
        flags=re.VERBOSE,
    )

    # Will match 59, 59+, 4-9, 3x5, 5-9+
    is_rst = re.fullmatch(
        r"""
            ^
            ([1-5])  # a number from 1 to 5 -- this is what we return
            [-x/]?  # optionally followed by an x, a dash, or a slash ( 5x9, 4-9, 3/5 )
            (?:\ by\ )?  # optionally followed by " by " ( 5 by 9 )
            [1-9]  # followed by a number from 1 to 9, which we throw away
            \+?  # optionally followed by a plus sign ( 59+ )
            $
        """,
        report,
        flags=re.VERBOSE,
    )

    if is_cm:
        return int(is_cm.group(1))
    if is_rst:
        return int(is_rst.group(1))
    return None  # if no match, return None


def score_competition(repeaters: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Score the competition and return the results.

    Parameters
    ----------
    repeaters : pd.DataFrame
        All the repeaters.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        _description_
    """

    if not logs_dir.exists():
        raise FileNotFoundError(f"{logs_dir} does not exist.")

    # Load the repeater data
    repeaters.index = repeaters["RR#"]

    # A mapping between RR# and club name
    rrn_to_club = repeaters["Group Name"].to_dict()

    # Calculate club-based multipliers
    club_n_repeaters = repeaters["Group Name"].value_counts().to_dict()

    all_logs = []
    contest_scores = {}

    for file in logs_files:

        callsign = file.stem.split(" ")[0].split(",")[0]
        logs = pd.read_csv(file, index_col=[0])
        n_entries = len(logs)

        # Clean up the log sheet
        logs = logs.astype({"Signal Report": str, "RR#": int})
        all_logs.append(logs.copy())  # save pre-deduped logs for activation counts
        logs = logs.drop_duplicates(subset=["RR#"], keep="first")
        n_duplicates = n_entries - len(logs)
        base_score = len(logs)

        # Add a group name column
        logs["Group Name"] = logs["RR#"].map(rrn_to_club)

        # Determine whether all repeaters from a club were worked
        worked = logs["Group Name"].value_counts().rename("Worked").to_frame()
        worked["Total"] = worked.index.map(club_n_repeaters)
        worked["All Repeaters Worked"] = worked["Worked"] == worked["Total"]
        worked["Bonus Eligible"] = worked["Total"] > 1

        # Calculate bonus points
        worked["Bonus Points"] = (
            worked["All Repeaters Worked"] * worked["Worked"] * worked["Bonus Eligible"]
        )
        bonus_points = worked["Bonus Points"].sum()

        # Save this person's contest scores
        contest_scores[callsign.upper()] = {
            "Entries": n_entries,
            "Duplicates": n_duplicates,
            "Base Score": base_score,
            "Bonus Points": bonus_points,
            "Total Score": base_score + bonus_points,
        }

    # Save the contest scores
    leaderboard = pd.DataFrame(contest_scores).T.sort_values("Total Score", ascending=False)
    print(leaderboard)
    leaderboard.to_csv("contest_scores.csv")

    # Merge all logs with repeater data
    repeater_cols = ["RR#", "Long Name", "Output (MHz)", "Location"]
    logs_df = (
        pd.concat(all_logs, ignore_index=True)
        .merge(repeaters[repeater_cols], left_on="RR#", right_index=True)
        .drop(columns=["RR#_x", "RR#_y"])
        .rename(columns={"Long Name": "Name", "Output (MHz)": "Frequency"})
        .astype({"Frequency": float})
    )

    # Attempt to clean up signal reports
    logs_df["Readability"] = logs_df["Signal Report"].apply(signal_report_to_readability)

    # Calculate the number of activations per repeater
    agg_cols = {
        "Name": "first",
        "Frequency": "first",
        "Time": "count",
        "Readability": "mean",
    }
    by_repeater = (
        logs_df.groupby("RR#")
        .agg(agg_cols)
        .rename(columns={"Time": "Activations", "Name": "Group"})
        .sort_values(["Activations", "Group", "Frequency"], ascending=False)
        .reset_index(drop=True)
        .round({"Readability": 2})
    )
    by_repeater.index = by_repeater.index + 1
    by_repeater.index.name = "Position"
    by_repeater["Frequency"] = by_repeater["Frequency"].round(3)

    # Calculate the number of activations per club
    by_club = (
        by_repeater.groupby("Group")["Activations"]
        .sum()
        .to_frame()
        .sort_values(["Activations", "Group"], ascending=[False, True])
        .reset_index(drop=False)  # index contains the club name
    )
    by_club.index = by_club.index + 1
    by_club.index.name = "Position"

    # TODO
    # Return dfs for scoring, repeater activations, and club activations
    return leaderboard, by_repeater.to_markdown(disable_numparse=True), by_club.to_markdown()
