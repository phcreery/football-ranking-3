from datetime import datetime
from typing import AsyncGenerator
from datastar_py.fastapi import (
    DatastarResponse,
    ReadSignals,
    ServerSentEventGenerator,
)
from datastar_py.sse import DatastarEvent
from fastapi import APIRouter
from fastapi.responses import FileResponse

from ..routers.scores import fetch_scores
from ..compute.rank import rank, filter_ranks
from ..config import logger

router = APIRouter()


@router.get("/")
async def handle_get_root():
    return FileResponse(
        "src/football_ranking/routers/static/index.html", media_type="text/html"
    )


def draw_settings(scores: list[dict]) -> str:
    current_year = datetime.now().year
    # get the last 4 years
    years = [current_year, current_year - 1, current_year - 2, current_year - 3]
    year_select = f"""
    <span id="year-options">
        <option value="{years[0]}">{years[0]}</option>
        <option value="{years[1]}">{years[1]}</option>
        <option value="{years[2]}">{years[2]}</option>
        <option value="{years[3]}">{years[3]}</option>
    </span>
    """
    # yield year_select
    # find all classifications in scores
    classifications = set()
    for score in scores:
        classifications.add(score["homeClassification"])
        classifications.add(score["awayClassification"])
    classification_select = f"""
    <span id="classification-options">
        <option selected>all</option>
        {"".join(f"<option>{c}</option>" for c in sorted(classifications))}
    </span>
    """
    # yield classification_select
    # find all conferences in scores
    conferences = set()
    for score in scores:
        conferences.add(score["homeConference"])
        conferences.add(score["awayConference"])
    conference_select = f"""
    <span id="conference-options">
        <option selected>all</option>
        {"".join(f"<option>{c}</option>" for c in sorted(conferences))}
    </span>
    """
    # yield conference_select
    return year_select + classification_select + conference_select


def draw_scores_table(scores: list[dict]):
    if not scores:
        return "<span>No games found</span>"

    table_rows = ""
    for game in scores:
        # just get the first yyy-mm-dd in startDate
        game["startDate"] = game["startDate"].split("T")[0]
        table_rows += f"""<tr>
            <td class="right-align">{game["startDate"]}</td>
            <td class="right-align">{game["homeClassification"]}</td>
            <td class="right-align">{game["homeConference"]}</td>
            <td class="right-align">{game["homeTeam"]}</td>
            <th class="right-align">{game["homePoints"]}</th>
            <th class="left-align">{game["awayPoints"]}</th>
            <td class="left-align">{game["awayTeam"]}</td>
            <td class="left-align">{game["awayConference"]}</td>
            <td class="left-align">{game["awayClassification"]}</td>
            <td class="left-align">{game["venue"]}</td>
        </tr>"""

    return f"""<div class="overflow-x-auto">
            <table class="table table-xs table-pin-rows">
                <thead>
                    <tr>
                        <th class="right-align">Date Played</th>
                        <th class="right-align">Div.</th>
                        <th class="right-align">Conference</th>
                        <th class="right-align">Home Team</th>
                        <th class="right-align">Home</th>
                        <th class="right-align">Away</th>
                        <th class="left-align">Away Team</th>
                        <th class="left-align">Away Conference</th>
                        <th class="left-align">Div.</th>
                        <th class="left-align">Venue</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>"""


def draw_ranks_table(ranks: list[dict]):
    if not ranks:
        return "<span>No rankings found</span>"

    table_rows = ""
    for team in ranks:
        table_rows += f"""<tr>
            <td class="right-align">{team["rank"]}</td>
            <td class="left-align">{team["team"]}</td>
            <td class="left-align">{team["classification"]}</td>
            <td class="left-align">{team["conference"]}</td>
            <td class="left-align">{team["rating"]}</td>
        </tr>"""

    return f"""<div class="overflow-x-auto">
            <table class="table table-xs table-pin-rows">
                <thead>
                    <tr>
                        <th class="right-align">Rank</th>
                        <th class="left-align">Team</th>
                        <th class="left-align">Division</th>
                        <th class="left-align">Conference</th>
                        <th class="left-align">Rating</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>"""


async def gen_load(
    year: int, classification: str, conference: str
) -> AsyncGenerator[DatastarEvent, None]:
    """Generate HTML for settings based on scores."""

    year = datetime.now().year
    yield ServerSentEventGenerator.patch_elements(
        """<span id="scores-table">
                    Loading Scores...
                </span>"""
    )
    scores = await fetch_scores(year, classification, conference)
    yield ServerSentEventGenerator.patch_elements(draw_settings(scores))
    yield ServerSentEventGenerator.patch_signals({"year": year})
    yield ServerSentEventGenerator.patch_elements(
        f"""<span id="scores-table">{draw_scores_table(scores)}</span>"""
    )


async def gen_scores(
    year: int, classification: str, conference: str
) -> AsyncGenerator[DatastarEvent, None]:
    """Generate a Server-Sent Event stream for scores."""
    # Unload both tables to avoid slow interactivity
    yield ServerSentEventGenerator.patch_elements(
        """<span id="ranks-table">
                    Loading Ranks...
                </span>"""
    )
    yield ServerSentEventGenerator.patch_elements(
        """<span id="scores-table">
                    Loading Scores...
                </span>"""
    )
    scores = await fetch_scores(year, classification, conference)
    yield ServerSentEventGenerator.patch_elements(
        f"""<span id="scores-table">{draw_scores_table(scores)}</span>"""
    )


async def gen_ranks(
    year: int, classification: str, conference: str
) -> AsyncGenerator[DatastarEvent, None]:
    """Generate a Server-Sent Event stream for ranks."""
    # Unload both tables to avoid slow interactivity
    yield ServerSentEventGenerator.patch_elements(
        """<span id="scores-table">
                    Loading Scores...
                </span>"""
    )
    yield ServerSentEventGenerator.patch_elements(
        """<span id="ranks-table">
                    Loading Ranks...
                </span>"""
    )
    # scores = await fetch_scores(year, classification, conference, exclusive=True)
    scores = await fetch_scores(year)
    ranking_dict = rank(scores)
    ranking_dict = filter_ranks(ranking_dict, classification, conference)
    # Here you would compute the ranks based on the scores
    # For now, we will just return the scores as a placeholder
    ranks = draw_ranks_table(ranking_dict)  # Replace with actual rank computation
    yield ServerSentEventGenerator.patch_elements(
        f"""<span id="ranks-table">{ranks}</span>"""
    )


def handle_signals(signals: ReadSignals):
    """Handle signals from the client."""
    logger.info(f"Received signals: {signals}")
    if not signals:
        raise ValueError(
            "No signals provided. Please provide 'year' and 'classification'."
        )
    year = signals.get("year", 2024)
    if isinstance(year, str):
        try:
            year = int(year)
        except ValueError:
            raise ValueError(f"Invalid year: {year}. Must be an integer.")
    classification = signals.get("classification", "fbs")
    if classification not in ["all", "fbs", "fcs", "ii"]:
        raise ValueError(
            f"Invalid classification: {classification}. Must be one of 'all', 'fbs', 'fcs', or 'ii'."
        )
    conference = signals.get("conference", "all")
    tab = signals.get("tab", "scores")
    if tab not in ["scores", "ranks"]:
        raise ValueError(f"Invalid tab: {tab}. Must be 'scores' or 'ranks'.")
    return year, classification, conference, tab


@router.get("/client/load")
async def handle_get_client_settings(signals: ReadSignals):
    # Handle client settings request.
    year, classification, conference, tab = handle_signals(signals)
    return DatastarResponse(gen_load(year, classification, conference))


@router.get("/client/reload")
async def handle_get_client_reload(signals: ReadSignals):
    if not signals:
        raise ValueError(
            "No signals provided. Please provide 'year' and 'classification'."
        )
    tab = signals.get("tab", "scores")
    if tab not in ["scores", "ranks"]:
        raise ValueError(f"Invalid tab: {tab}. Must be 'scores' or 'ranks'.")
    year, classification, conference, tab = handle_signals(signals)
    if tab == "scores":
        return DatastarResponse(gen_scores(year, classification, conference))
    else:
        return DatastarResponse(gen_ranks(year, classification, conference))


@router.get("/client/scores")
async def handle_get_client_scores(signals: ReadSignals):
    year, classification, conference, tab = handle_signals(signals)
    return DatastarResponse(gen_scores(year, classification, conference))


@router.get("/client/ranks")
async def handle_get_client_ranks(signals: ReadSignals):
    year, classification, conference, tab = handle_signals(signals)
    return DatastarResponse(gen_ranks(year, classification, conference))
