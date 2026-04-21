"""
Módulo de evaluación del sistema recomendador.

Metodología: Hold-Out 80/20 sobre usuarios de prueba generados por arquetipos.
Métricas (via rectools): HitRate, NDCG, Precision, Recall, CatalogCoverage, IntraListDiversity, Serendipity.

"""

import random
import sys
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt

from rectools import Columns as RC
from rectools.metrics import (
    HitRate,
    NDCG,
    Precision,
    Recall,
    CatalogCoverage,
    IntraListDiversity,
    Serendipity,
    calc_metrics,
)
from rectools.metrics.distances import PairwiseHammingDistanceCalculator

# ----- configuración del path para importar módulos de la app -----
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
from app.logics.games_logic import read_games_df
from app.logics.users_logic import (
    build_user_from_row,
    get_user_preference_vector,
    get_game_genre_value,
    get_new_user_preference_value,
    get_empty_user_attributes,
    read_users_df,
)
from app.logics.preferences_logic import read_preferences_df
from app.logics.recommendations_logic import (
    get_content_score,
    get_base_score,
    get_serendipity_score,
    get_game_score,
    get_similarity_between_users,
    get_random_recommendation_sample,
    transform_collaborative_ranking,
)
from app.models import User, UserAttributes

# ----- parametros -----

N_USERS_PER_ARCHETYPE = 10
N_PREFS_PER_USER      = 15
K_RECS                = 10
HOLD_OUT_RATIO        = 0.20
RANDOM_SEED           = 42

ARCHETYPES = [
    {"name": "Perfil RPG",
     "action_preference": 2.0, "adventure_preference": 7.0, "platformer_preference": 2.0,
     "puzzle_horror_preference": 1.0, "rpg_preference": 10.0, "racing_preference": 0.0,
     "shooter_preference": 1.0, "simulation_preference": 1.0, "sports_preference": 0.0,
     "strategy_preference": 5.0},
    {"name": "Perfil Accion",
     "action_preference": 9.0, "adventure_preference": 5.0, "platformer_preference": 3.0,
     "puzzle_horror_preference": 2.0, "rpg_preference": 2.0, "racing_preference": 2.0,
     "shooter_preference": 8.0, "simulation_preference": 1.0, "sports_preference": 1.0,
     "strategy_preference": 2.0},
    {"name": "Perfil Plataformas",
     "action_preference": 4.0, "adventure_preference": 6.0, "platformer_preference": 10.0,
     "puzzle_horror_preference": 5.0, "rpg_preference": 3.0, "racing_preference": 1.0,
     "shooter_preference": 1.0, "simulation_preference": 1.0, "sports_preference": 0.0,
     "strategy_preference": 1.0},
    {"name": "Perfil Estrategia",
     "action_preference": 2.0, "adventure_preference": 3.0, "platformer_preference": 1.0,
     "puzzle_horror_preference": 3.0, "rpg_preference": 4.0, "racing_preference": 1.0,
     "shooter_preference": 2.0, "simulation_preference": 7.0, "sports_preference": 1.0,
     "strategy_preference": 10.0},
    {"name": "Perfil Deportes",
     "action_preference": 3.0, "adventure_preference": 1.0, "platformer_preference": 1.0,
     "puzzle_horror_preference": 0.0, "rpg_preference": 0.0, "racing_preference": 8.0,
     "shooter_preference": 2.0, "simulation_preference": 5.0, "sports_preference": 10.0,
     "strategy_preference": 1.0},
]

# ----- funciones que necesitan dataframes en memoria -----

def get_collaborative_score_from_df(
    user: User,
    game_id: int,
    prefs_df: pd.DataFrame,
    users_df: pd.DataFrame,
) -> float:
    """
    Calcula el score colaborativo para un usuario y juego dado usando DataFrames.
    """
    game_prefs = prefs_df[prefs_df[config.PREFERENCE_ITEM_ID_COLUMN] == game_id]

    if game_prefs.empty:
        return 0.0

    total_weighted_score = 0.0
    total_similarity     = 0.0

    for _, preference in game_prefs.iterrows():
        other_user_id = int(preference[config.PREFERENCE_USER_ID_COLUMN])

        if other_user_id == user.id:
            continue

        other_rows = users_df[users_df[config.USER_ID_COLUMN] == other_user_id]
        if other_rows.empty:
            continue

        other_user  = build_user_from_row(other_rows.iloc[0])
        similarity  = get_similarity_between_users(user, other_user)
        ranking     = int(float(preference[config.PREFERENCE_RANKING_COLUMN]))
        transformed = transform_collaborative_ranking(ranking)

        total_weighted_score += similarity * transformed
        total_similarity     += abs(similarity)

    if total_similarity == 0:
        return 0.0

    return total_weighted_score / total_similarity


def get_final_score_from_df(
    user: User,
    game_row: pd.Series,
    prefs_df: pd.DataFrame,
    users_df: pd.DataFrame,
) -> float:
    """
    Calcula el score final para un usuario y juego dado usando DataFrames.
    """
    game_id = int(game_row[config.GAME_ID_COLUMN])

    content_score      = get_content_score(user, game_row)
    collaborative_score = get_collaborative_score_from_df(user, game_id, prefs_df, users_df)
    base_score         = get_base_score(content_score, collaborative_score)
    serendipity        = get_serendipity_score(content_score, game_row)
    game_score         = get_game_score(game_row)

    beta  = config.RECOMMENDATION_SERENDIPITY_WEIGHT
    gamma = config.RECOMMENDATION_GAME_SCORE_WEIGHT

    combined = (1 - beta) * base_score + beta * serendipity
    return (1 - gamma) * combined + gamma * game_score


def get_recommendations_from_df(
    user: User,
    rated_ids: set[int],
    prefs_df: pd.DataFrame,
    users_df: pd.DataFrame,
    games_df: pd.DataFrame,
    k: int = K_RECS,
) -> list[int]:
    """
    Genera recomendaciones para un usuario dado usando DataFrames.
    """
    scored_games = []

    for _, game_row in games_df.iterrows():
        game_id = int(game_row[config.GAME_ID_COLUMN])

        if game_id in rated_ids:
            continue

        score = get_final_score_from_df(user, game_row, prefs_df, users_df)
        scored_games.append({"score": score, "row": game_row})

    scored_games.sort(key=lambda g: g["score"], reverse=True)

    candidate_pool = scored_games[:max(k, k * 2)]
    selected       = get_random_recommendation_sample(candidate_pool, k)

    return [int(g["row"][config.GAME_ID_COLUMN]) for g in selected]

# ----- reconstruccion de perfil desde preferencias -----

def rebuild_user_from_ratings(
    user_id: int,
    ratings: list[tuple[int, int]],
    games_df: pd.DataFrame,
) -> User:
    """
    Reconstruye un objeto User a partir de sus preferencias (game_id, ranking). 
    """
    attrs = get_empty_user_attributes()

    for game_id, ranking in ratings:
        g_rows = games_df[games_df[config.GAME_ID_COLUMN] == game_id]
        if g_rows.empty:
            continue
        game_row = g_rows.iloc[0]
        for genre_name, user_col in config.GAME_TO_USER_ATTRIBUTE_MAP.items():
            game_value      = get_game_genre_value(game_row, genre_name)
            attrs[user_col] = get_new_user_preference_value(attrs[user_col], game_value, ranking)

    return User(
        id=user_id,
        username=f"eval_{user_id}",
        attributes=UserAttributes(**attrs),
    )

# ----- generacion de usuarios de prueba -----

def generate_prefs_for_user(
    user: User,
    games_df: pd.DataFrame,
    n: int,
    seed: int,
) -> list[tuple[int, int]]:
    """
    Genera una lista de preferencias (game_id, ranking) para un usuario dado.
    """
    rng = random.Random(seed)

    scored = []
    for _, game_row in games_df.iterrows():
        cs    = get_content_score(user, game_row)
        noise = rng.gauss(0, 0.08)
        score = max(0.0, min(1.0, cs + noise))
        scored.append((score, int(game_row[config.GAME_ID_COLUMN])))

    scored.sort(reverse=True)
    candidates = scored[:min(n * 2, len(scored))]
    selected   = rng.sample(candidates, min(n, len(candidates)))

    result = []
    for sc, gid in selected:
        ranking = 5 if sc > 0.70 else (4 if sc > 0.50 else (3 if sc > 0.30 else (2 if sc > 0.10 else 1)))
        result.append((gid, ranking))

    return result


def build_test_users(
    games_df: pd.DataFrame,
    n_per_archetype: int = N_USERS_PER_ARCHETYPE,
    n_prefs: int = N_PREFS_PER_USER,
    start_uid: int = 9000,
) -> list[dict]:
    """
    Genera usuarios de prueba a partir de arquetipos definidos en ARCHETYPES.
    """
    all_synthetic = []
    uid = start_uid

    for arch in ARCHETYPES:
        base_attrs = {k: v for k, v in arch.items() if k != "name"}
        for _ in range(n_per_archetype):
            noisy_attrs = {
                col: max(0.0, min(10.0, val + random.gauss(0, 0.6)))
                for col, val in base_attrs.items()
            }
            base_user = User(
                id=uid,
                username=f"eval_{uid}",
                attributes=UserAttributes(**noisy_attrs),
            )
            prefs = generate_prefs_for_user(base_user, games_df, n_prefs, seed=uid)
            all_synthetic.append({
                "uid":       uid,
                "archetype": arch["name"],
                "user":      base_user,
                "prefs":     prefs,
            })
            uid += 1

    return all_synthetic


def build_extended_dataframes(
    all_synthetic: list[dict],
    real_users_df: pd.DataFrame,
    real_prefs_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Construye DataFrames extendidos de usuarios y preferencias combinando reales y de prueba.
    """
    synth_user_rows = []
    synth_pref_rows = []

    for su in all_synthetic:
        row = {
            config.USER_ID_COLUMN:  su["uid"],
            config.USERNAME_COLUMN: su["user"].username,
            **{col: float(getattr(su["user"].attributes, col))
               for col in config.USER_ATTRIBUTE_COLUMNS},
        }
        synth_user_rows.append(row)
        for gid, ranking in su["prefs"]:
            synth_pref_rows.append({
                config.PREFERENCE_USER_ID_COLUMN: su["uid"],
                config.PREFERENCE_ITEM_ID_COLUMN: gid,
                config.PREFERENCE_RANKING_COLUMN: ranking,
            })

    extended_users = pd.concat([real_users_df, pd.DataFrame(synth_user_rows)], ignore_index=True)
    extended_prefs = pd.concat([real_prefs_df, pd.DataFrame(synth_pref_rows)], ignore_index=True)

    return extended_users, extended_prefs

# ----- helpers rectools -----

def build_genre_features_df(games_df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye un DataFrame de características de género para los juegos, usado en el cálculo de ILD.
    """
    genre_cols = list(config.GAME_TO_USER_ATTRIBUTE_MAP.keys())
    features = games_df[[config.GAME_ID_COLUMN] + genre_cols].copy()
    features = features.set_index(config.GAME_ID_COLUMN)
    return features.astype(float)


# ----- bucle de evaluacion hold-out -----

def evaluate(
    all_synthetic: list[dict],
    extended_users_df: pd.DataFrame,
    extended_prefs_df: pd.DataFrame,
    games_df: pd.DataFrame,
    all_game_ids: set[int],
    k: int = K_RECS,
    hold_out_ratio: float = HOLD_OUT_RATIO,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Ejecuta el proceso completo de evaluación Hold-Out para los usuarios de prueba.
    """
    results    = []
    reco_rows  = []
    test_rows  = []
    train_rows = []

    for su in all_synthetic:
        all_prefs = su["prefs"]
        if len(all_prefs) < 2:
            continue

        split_idx   = max(1, int(len(all_prefs) * (1 - hold_out_ratio)))
        train_prefs = all_prefs[:split_idx]
        test_prefs  = all_prefs[split_idx:]

        if not test_prefs:
            continue

        train_ids = set(gid for gid, _ in train_prefs)
        test_ids  = set(gid for gid, _ in test_prefs)

        train_user = rebuild_user_from_ratings(su["uid"], train_prefs, games_df)

        eval_prefs = extended_prefs_df[
            ~(
                (extended_prefs_df[config.PREFERENCE_USER_ID_COLUMN] == su["uid"]) &
                (extended_prefs_df[config.PREFERENCE_ITEM_ID_COLUMN].isin(test_ids))
            )
        ].copy()

        try:
            recs = get_recommendations_from_df(
                train_user, train_ids, eval_prefs, extended_users_df, games_df, k=k
            )
        except Exception:
            continue

        for rank, gid in enumerate(recs, 1):
            reco_rows.append({RC.User: su["uid"], RC.Item: gid, RC.Rank: rank})
        for gid, _ in test_prefs:
            test_rows.append({RC.User: su["uid"], RC.Item: gid})
        for gid, _ in train_prefs:
            train_rows.append({RC.User: su["uid"], RC.Item: gid})

        results.append({
            "uid":       su["uid"],
            "archetype": su["archetype"],
            "n_train":   len(train_ids),
            "n_test":    len(test_ids),
            "n_recs":    len(set(recs)),
        })

    reco_df  = pd.DataFrame(reco_rows)
    test_df  = pd.DataFrame(test_rows)
    train_df = pd.DataFrame(train_rows)

    return pd.DataFrame(results), reco_df, test_df, train_df

# ----- reporte y graficos -----

def print_report(
    results_df: pd.DataFrame,
    reco_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_df: pd.DataFrame,
    games_df: pd.DataFrame,
    all_game_ids: set[int],
) -> None:
    catalog = list(all_game_ids)
    genre_features = build_genre_features_df(games_df)
    dist_calc = PairwiseHammingDistanceCalculator(genre_features)

    global_metrics = calc_metrics(
        {
            f"HitRate@{K_RECS}":     HitRate(k=K_RECS),
            f"NDCG@{K_RECS}":        NDCG(k=K_RECS),
            f"Precision@{K_RECS}":   Precision(k=K_RECS),
            f"Recall@{K_RECS}":      Recall(k=K_RECS),
            f"Coverage@{K_RECS}":    CatalogCoverage(k=K_RECS, normalize=True),
            f"ILD@{K_RECS}":         IntraListDiversity(k=K_RECS, distance_calculator=dist_calc),
            f"Serendipity@{K_RECS}": Serendipity(k=K_RECS),
        },
        reco=reco_df,
        interactions=test_df,
        prev_interactions=train_df,
        catalog=catalog,
    )

    print("=" * 60)
    print("        RESULTADOS DE EVALUACIÓN DEL MODELO")
    print("=" * 60)
    print(f"  Usuarios evaluados            : {len(results_df)}")
    for name, val in global_metrics.items():
        print(f"  {name:<30}: {val:.4f}")
    print("=" * 60)

    # Métricas por arquetipo
    uid_to_arch = results_df.set_index("uid")["archetype"].to_dict()

    hit_pu   = HitRate(k=K_RECS).calc_per_user(reco_df, test_df).rename("hit")
    ndcg_pu  = NDCG(k=K_RECS).calc_per_user(reco_df, test_df).rename("ndcg")
    ild_pu   = IntraListDiversity(k=K_RECS, distance_calculator=dist_calc).calc_per_user(reco_df).rename("ild")
    seren_pu = Serendipity(k=K_RECS).calc_per_user(reco_df, test_df, train_df, catalog).rename("serendipity")

    per_user_df = pd.concat([hit_pu, ndcg_pu, ild_pu, seren_pu], axis=1)
    per_user_df["archetype"] = per_user_df.index.map(uid_to_arch)

    arch_stats = per_user_df.groupby("archetype")[["hit", "ndcg", "ild", "serendipity"]].mean().reset_index()
    n_per_arch = results_df.groupby("archetype")["uid"].count().rename("n").reset_index()
    arch_stats = arch_stats.merge(n_per_arch, on="archetype")

    print("\nResultados por arquetipo:")
    print("-" * 90)
    for _, row in arch_stats.iterrows():
        print(f"  {row['archetype']:<22}  Hit: {row['hit']*100:5.1f}%"
              f"  NDCG: {row['ndcg']:.4f}"
              f"  ILD: {row['ild']:.4f}"
              f"  Serendipity: {row['serendipity']:.4f}"
              f"  (n={int(row['n'])})")

    _plot(arch_stats, global_metrics)


def _plot(arch_stats: pd.DataFrame, global_metrics: dict) -> None:
    fig, axes = plt.subplots(1, 4, figsize=(22, 5))
    fig.suptitle("Evaluación del Sistema Recomendador — Hold-Out 80/20 (RecTools)",
                 fontsize=14, fontweight="bold")
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]
    x = range(len(arch_stats))

    specs = [
        ("hit",         f"HitRate@{K_RECS}",     "Hit Rate [0–1]"),
        ("ndcg",        f"NDCG@{K_RECS}",         "NDCG [0–1]"),
        ("ild",         f"ILD@{K_RECS}",           "ILD [0–1]"),
        ("serendipity", f"Serendipity@{K_RECS}",   "Serendipity"),
    ]

    for ax, (col, title, ylabel) in zip(axes, specs):
        vals = arch_stats[col]
        avg  = global_metrics.get(title, vals.mean())
        bars = ax.bar(x, vals, color=colors)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        max_v = max(vals.max(), 0.01)
        ax.set_ylim(0, min(max_v * 1.35, 1.05))
        ax.axhline(avg, color="black", linestyle="--", linewidth=1.2,
                   label=f"Promedio: {avg:.4f}")
        ax.legend(fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels(arch_stats["archetype"], rotation=20, ha="right", fontsize=9)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max_v * 0.02,
                    f"{val:.3f}", ha="center", fontsize=8)

    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), "..", "notebooks", "images", "evaluacion_modelo.png")
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"Gráfico guardado en {os.path.normpath(output_path)}")

# ----- entry point -----

def main():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    print("Cargando datos...")
    games_df      = read_games_df()
    real_users_df = read_users_df()
    real_prefs_df = read_preferences_df()
    all_game_ids  = set(games_df[config.GAME_ID_COLUMN].astype(int).tolist())

    print(f"  Catálogo: {len(all_game_ids)} juegos | Usuarios reales: {len(real_users_df)}")

    print(f"\nGenerando {N_USERS_PER_ARCHETYPE * len(ARCHETYPES)} usuarios de prueba...")
    all_synthetic = build_test_users(games_df)

    extended_users_df, extended_prefs_df = build_extended_dataframes(
        all_synthetic, real_users_df, real_prefs_df
    )
    print(f"  Dataset extendido: {len(extended_users_df)} usuarios | {len(extended_prefs_df)} preferencias")

    print(f"\nEjecutando evaluación Hold-Out {int((1-HOLD_OUT_RATIO)*100)}/{int(HOLD_OUT_RATIO*100)}...")
    results_df, reco_df, test_df, train_df = evaluate(
        all_synthetic, extended_users_df, extended_prefs_df, games_df, all_game_ids
    )

    print()
    print_report(results_df, reco_df, test_df, train_df, games_df, all_game_ids)


if __name__ == "__main__":
    main()
