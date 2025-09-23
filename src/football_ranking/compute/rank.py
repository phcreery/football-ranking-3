from typing import Any
from ..config import logger

import numpy as np
from scipy.linalg import null_space
import sympy as sp


def compute_ranking(M):
    # Sum of the columns in 1D matrix
    colsum = np.sum(M, axis=0)
    # Subtract games matrix with diagonal matrix of column sum
    diff = M - np.diag(colsum)
    # compute null-space matrix of the difference
    ranking_matrix = null_space(diff)
    # Take the absolute value of the array
    ranking_matrix = np.absolute(ranking_matrix)
    # print("ranking matrix", ranking_matrix)

    # Quick-fix for when null_space returns a matrix size of (x,>1) instead of expected (x,1)
    if ranking_matrix.shape[1] != 1:
        # print("uh oh, no bueno")
        new_ranking_matrix = np.array([])
        for row in ranking_matrix:
            best_cell = 0
            # print(row)
            for cell in row:
                if cell > best_cell:
                    best_cell = cell
            new_value = np.array([best_cell])
            # print(new_value)
            new_ranking_matrix = np.append(new_ranking_matrix, new_value, axis=0)
        # print("new matrix", len(new_ranking_matrix), new_ranking_matrix)
        ranking_matrix = new_ranking_matrix

    # Convert to a python List
    ranking = ranking_matrix.flatten().tolist()
    return ranking


def weird_division(n, d):
    return n / d if d else 0


def find_linearly_independent_columns_qr(matrix, tolerance=1e-9):
    """
    Identifies a set of linearly independent columns using QR decomposition.

    Args:
        matrix (np.ndarray): The input matrix.
        tolerance (float): A threshold to consider diagonal elements of R as zero.

    Returns:
        list: A list of indices of linearly independent columns.
    """
    Q, R, P = np.linalg.qr(matrix, mode="economic", pivoting=True)
    # The diagonal elements of R indicate the "importance" of the corresponding columns.
    # Columns corresponding to large diagonal elements are linearly independent.
    # P is the permutation array, indicating the order of columns after pivoting.

    independent_column_indices = P[np.abs(np.diag(R)) > tolerance]
    return independent_column_indices


def rank(data: list[Any]):
    logger.info("Ranking data...")
    # logger.info(data)
    # Generate Teams list
    teams = []
    classifications = []
    conferences = []
    for game in data:
        if game["homeTeam"] not in teams:
            teams.append(game["homeTeam"])
            classifications.append(game["homeClassification"])
            conferences.append(game["homeConference"])

        if game["awayTeam"] not in teams:
            teams.append(game["awayTeam"])
            classifications.append(game["awayClassification"])
            conferences.append(game["awayConference"])

    # Generate game matrix
    M_offense = np.zeros((len(teams), len(teams)), dtype=int)
    for game in data:
        i = teams.index(game["homeTeam"])
        j = teams.index(game["awayTeam"])
        M_offense[i, j] = game["homePoints"] if game["homePoints"] is not None else 0
        M_offense[j, i] = game["awayPoints"] if game["awayPoints"] is not None else 0
    M_defense = np.transpose(M_offense)

    # print(M_offense)
    # print(M_defense)
    # with np.printoptions(threshold=np.inf):
    #   print(M_offense)
    #   print(M_defense)
    # determinant_offense = np.linalg.det(M_offense)
    # print(f"Determinant Offense: {determinant_offense}")
    # determinant_defense = np.linalg.det(M_defense)
    # print(f"Determinant Defense: {determinant_defense}")

    # go through each row and check if all values are zero
    # zero_rows_offense = []
    # for i, row in enumerate(M_offense):
    #     # print(f"Row {i}: {row}")
    #     if np.all(row == 0):
    #         print(f"Row {i} is all zeros in Offense matrix")
    #         zero_rows_offense.append(i)
    # zero_rows_defense = []
    # for i, row in enumerate(M_defense):
    #     # print(f"Row {i}: {row}")
    #     if np.all(row == 0):
    #         print(f"Row {i} is all zeros in Defense matrix")
    #         zero_rows_defense.append(i)
    # # go through each col and check if all values are zero
    # zero_cols_offense = []
    # for i in range(M_offense.shape[1]):
    #     if np.all(M_offense[:, i] == 0):
    #         print(f"Col {i} is all zeros in Offense matrix")
    #         zero_cols_offense.append(i)
    # zero_cols_defense = []
    # for i in range(M_defense.shape[1]):
    #     if np.all(M_defense[:, i] == 0):
    #         print(f"Col {i} is all zeros in Defense matrix")
    #         zero_cols_defense.append(i)

    # Offense Rankings
    rank_offense = compute_ranking(M_offense)
    # print(f"Rank Offense: {rank_offense} ({len(rank_offense)})")
    # rank_offense_rank = np.linalg.matrix_rank(M_offense, tol=2)
    # print(f"Rank Offense Rank: {rank_offense_rank} ({len(rank_offense)})")

    # Defense Rankings
    rank_defense = compute_ranking(M_defense)
    # print(f"Rank Defense: {rank_defense} ({len(rank_defense)})")
    # rank_defense_rank = np.linalg.matrix_rank(M_defense, tol=2)
    # print(f"Rank Defense Rank: {rank_defense_rank} ({len(rank_defense)})")

    M_offense_svd = np.linalg.svd(a=M_offense)
    with np.printoptions(threshold=np.inf):
        print(f"Offense SVD: {M_offense_svd[1]}")

    # Find linearly independent columns using QR decomposition
    # _, inds = sp.Matrix(M_offense).rref()
    # print(f"Linearly independent columns Offense: {inds} (length {len(inds)})")
    # _, inds = sp.Matrix(M_offense).T.rref()
    # print(f"Linearly independent rows Offense: {inds} (length {len(inds)})")

    # Combine Offense and Defense Rankings
    ranking = [weird_division(i, j) for i, j in zip(rank_offense, rank_defense)]

    # Create dict and combine values of teams and ranking
    # ranking_dict = {}
    # print(ranking)
    # for i, rank in enumerate(ranking):
    #     ranking_dict[teams[i]] = rank

    # Create array of teams and ranking
    ranking_dict = [
        {
            "team": team,
            "rating": rank,
            "classification": classification,
            "conference": conference,
        }
        for team, rank, classification, conference in zip(
            teams, ranking, classifications, conferences
        )
    ]

    # Sort the array by rating
    ranking_dict = sorted(ranking_dict, key=lambda k: k["rating"], reverse=True)
    # add rank to the dict
    for i, team in enumerate(ranking_dict):
        team["rank"] = i + 1

    # print(ranking_dict)
    return ranking_dict


def filter_ranks(
    ranking_dict: list[dict], classification: str | None, conference: str | None
) -> list[dict]:
    if conference and conference != "all":
        ranking_dict = [
            game for game in ranking_dict if game["conference"] == conference
        ]
    if classification and classification != "all":
        ranking_dict = [
            game for game in ranking_dict if game["classification"] == classification
        ]

    # logger.info(f"Filtered ranks: {len(ranking_dict)}")
    return ranking_dict
