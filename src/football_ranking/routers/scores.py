from fastapi import APIRouter, HTTPException
import httpx
import urllib.parse

from ..config import logger, app_config
from ..compute.rank import rank

router = APIRouter()


async def patch_filter_scores(
    scores: list[dict],
    classification: str | None,
    conference: str | None,
    exclusive: bool = False,
) -> list[dict]:
    if exclusive:
        if conference and conference != "all":
            scores = [
                game
                for game in scores
                if game["homeConference"] == conference
                and game["awayConference"] == conference
            ]
        if classification and classification != "all":
            scores = [
                game
                for game in scores
                if game["homeClassification"] == classification
                and game["awayClassification"] == classification
            ]
    else:
        if conference and conference != "all":
            scores = [
                game
                for game in scores
                if game["homeConference"] == conference
                or game["awayConference"] == conference
            ]
        if classification and classification != "all":
            scores = [
                game
                for game in scores
                if game["homeClassification"] == classification
                or game["awayClassification"] == classification
            ]
    # print(scores)
    scores = [
        game
        for game in scores
        if game["homeTeam"] != "Brown" and game["awayTeam"] != "Brown"
    ]
    # logger.info(f"Filtered scores: {len(scores)} games for conference {conference}")
    return scores


async def fetch_scores(
    year: int,
    classification: str | None = None,
    conference: str | None = None,
    exclusive: bool = False,
) -> list[dict]:
    """Fetch scores for a given year and classification."""
    URL = f"https://api.collegefootballdata.com:443/games?year={year}"

    if classification and classification != "all":
        URL += "&classification=" + urllib.parse.quote(classification)

    # if conference and conference != "all":
    #     URL += "&conference=" + urllib.parse.quote(conference)

    logger.info(f"Fetching scores from URL: {URL}")

    # Load token from environment variable
    token = app_config.CFBD__API_TOKEN
    logger.info(
        f"Using token: {token[:4]}..."
    )  # Log only the first 4 characters for security

    authorization = f"Bearer {token}"

    headers = {
        "Authorization": authorization,
        "X-Requested-With": "https://peyton.creery.org/",
    }

    scores = {}
    async with httpx.AsyncClient() as client:
        resp = await client.get(URL, headers=headers)
        logger.info(f"Response status code: {resp.status_code}")
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Error fetching data: {resp.text}",
            )
        logger.info(f"Response: {resp.text[:100]}...")  # Log first 100 characters
        scores = resp.json()

        # Filter out division III games
        allowed_divisions = ["fbs", "fcs", "ii"]
        scores = [
            game
            for game in scores
            if (game["homeClassification"] in allowed_divisions)
            and (game["awayClassification"] in allowed_divisions)
        ]

    scores = await patch_filter_scores(scores, classification, conference, exclusive)

    return scores


@router.get("/scores/{year}")
async def get_scores(year: int, classification: str | None):
    try:
        scores = await fetch_scores(year, classification)
        # logger.info(f"Scores for {year}: {scores}")
        return scores
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=400, detail=f"Error: {e}")


@router.get("/ranking/{year}")
async def get_ranking(year: int, classification: str | None):
    try:
        scores = await fetch_scores(year, classification)
        ranking_dict = rank(scores)
        return ranking_dict

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=400, detail=f"Error: {e}")
