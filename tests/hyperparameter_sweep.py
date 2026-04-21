"""
Barrido de hiperparámetros del sistema recomendador.
Métricas (via rectools): HitRate, NDCG, Precision, Recall, CatalogCoverage,
IntraListDiversity, Serendipity.
"""

import importlib
import os
import pkgutil
import random
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
import tests.model_evaluation as ev
import tests.configs as configs_pkg
from app.logics.games_logic import read_games_df
from app.logics.users_logic import read_users_df
from app.logics.preferences_logic import read_preferences_df
from rectools.metrics import (
    HitRate, NDCG, Precision, Recall,
    CatalogCoverage, IntraListDiversity, Serendipity,
    calc_metrics,
)
from rectools.metrics.distances import PairwiseHammingDistanceCalculator

RANDOM_SEED = 42

# ----- carga dinamica de configs -----

def load_all_configs() -> list[dict]:
    """
    Mira y carga todos los módulos dentro de tests/configs/ (excepto __init__).
    Retorna una lista de dicts con esos tres campos más el nombre del módulo.
    """
    configs = []
    configs_path = os.path.dirname(configs_pkg.__file__)

    for finder, module_name, _ in pkgutil.iter_modules([configs_path]):
        full_name = f"tests.configs.{module_name}"
        mod = importlib.import_module(full_name)
        configs.append({
            "module":      module_name,
            "name":        mod.NAME,
            "description": mod.DESCRIPTION,
            "params":      mod.PARAMS,
        })

    # Orden fijo: baseline primero, luego el resto alfabéticamente
    configs.sort(key=lambda c: (0 if c["module"] == "baseline" else 1, c["module"]))
    return configs


# ----- parcheo temporal de config -----

class ConfigPatch:
    """
    Context manager que sobreescribe atributos de config para una ejecucion
    y los restaura al salir.

        with ConfigPatch({"RECOMMENDATION_CONTENT_WEIGHT": 0.9}):
            ...  # config usa los nuevos valores
        # config restaurado
    """
    def __init__(self, params: dict):
        self.params   = params
        self.originals = {}

    def __enter__(self):
        for key, value in self.params.items():
            self.originals[key] = getattr(config, key)
            setattr(config, key, value)
        return self

    def __exit__(self, *_):
        for key, original in self.originals.items():
            setattr(config, key, original)


# ----- ejecucion de una ejecucion -----

def run_single(
    cfg: dict,
    games_df: pd.DataFrame,
    real_users_df: pd.DataFrame,
    real_prefs_df: pd.DataFrame,
    all_game_ids: set[int],
    dist_calc: PairwiseHammingDistanceCalculator,
) -> dict:
    """
    Aplica los parámetros de cfg, ejecuta el pipeline completo de evaluación
    y devuelve un dict con las métricas de RecTools para esa configuración.
    """
    print(f"\n{'-' * 58}")
    print(f"  Config: {cfg['name']}  —  {cfg['description']}")
    print(f"  Params: { {k: v for k, v in cfg['params'].items()} }")
    print(f"{'-' * 58}")

    with ConfigPatch(cfg["params"]):
        random.seed(RANDOM_SEED)
        np.random.seed(RANDOM_SEED)

        all_test_users = ev.build_test_users(games_df)
        extended_users_df, extended_prefs_df = ev.build_extended_dataframes(
            all_test_users, real_users_df, real_prefs_df
        )
        results_df, reco_df, test_df, train_df = ev.evaluate(
            all_test_users, extended_users_df, extended_prefs_df, games_df, all_game_ids
        )

    catalog = list(all_game_ids)
    k = ev.K_RECS
    metrics = calc_metrics(
        {
            f"HitRate@{k}":     HitRate(k=k),
            f"NDCG@{k}":        NDCG(k=k),
            f"Precision@{k}":   Precision(k=k),
            f"Recall@{k}":      Recall(k=k),
            f"Coverage@{k}":    CatalogCoverage(k=k, normalize=True),
            f"ILD@{k}":         IntraListDiversity(k=k, distance_calculator=dist_calc),
            f"Serendipity@{k}": Serendipity(k=k),
        },
        reco=reco_df,
        interactions=test_df,
        prev_interactions=train_df,
        catalog=catalog,
    )

    for name, val in metrics.items():
        print(f"  {name:<20}: {val:.4f}")

    return {"config": cfg["name"], **metrics, **{k: v for k, v in cfg["params"].items()}}


# ----- reporte y grafico comparativo -----

def print_summary(sweep_df: pd.DataFrame) -> None:
    k = ev.K_RECS
    metric_cols = [
        f"HitRate@{k}", f"NDCG@{k}", f"Precision@{k}", f"Recall@{k}",
        f"Coverage@{k}", f"ILD@{k}", f"Serendipity@{k}",
    ]
    print("\n" + "=" * 80)
    print("  RESUMEN DEL BARRIDO DE HIPERPARÁMETROS")
    print("=" * 80)
    print(sweep_df[["config"] + metric_cols].to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print()
    for col in metric_cols:
        best = sweep_df.loc[sweep_df[col].idxmax(), "config"]
        print(f"  Mejor {col:<20}: {best}")
    print("=" * 80)


def _plot_sweep(sweep_df: pd.DataFrame) -> None:
    k = ev.K_RECS
    metrics = [
        (f"HitRate@{k}",     f"HitRate@{k}"),
        (f"NDCG@{k}",        f"NDCG@{k}"),
        (f"Coverage@{k}",    f"Coverage@{k}"),
        (f"ILD@{k}",         f"ILD@{k}"),
        (f"Serendipity@{k}", f"Serendipity@{k}"),
    ]

    fig, axes = plt.subplots(1, len(metrics), figsize=(5 * len(metrics), 6))
    fig.suptitle("Barrido de Hiperparámetros. Comparación de configuraciones (RecTools)",
                 fontsize=13, fontweight="bold")

    palette = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2",
               "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD"]

    x      = range(len(sweep_df))
    labels = sweep_df["config"].tolist()
    colors = palette[:len(sweep_df)]

    for ax, (col, title) in zip(axes, metrics):
        values = sweep_df[col].tolist()
        bars   = ax.bar(x, values, color=colors)
        ax.set_title(title, fontsize=11)
        ax.set_ylabel(title, fontsize=9)
        max_v = max(values) if values else 0.01
        ax.set_ylim(0, min(max_v * 1.35, 1.05))

        avg = sum(values) / len(values)
        ax.axhline(avg, color="black", linestyle="--", linewidth=1.1,
                   label=f"Prom: {avg:.4f}")
        ax.legend(fontsize=8)
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max_v * 0.02,
                    f"{val:.4f}", ha="center", fontsize=7.5)

    plt.tight_layout()
    out = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "notebooks", "images", "hyperparameter_sweep.png"
    ))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    plt.savefig(out, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"\nGráfico guardado en {out}")


# ----- entry point -----

def run_sweep() -> pd.DataFrame:
    """
    Ejecuta el barrido completo. Retorna el DataFrame de resultados.
    """
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    print("Cargando datos base...")
    games_df      = read_games_df()
    real_users_df = read_users_df()
    real_prefs_df = read_preferences_df()
    all_game_ids  = set(games_df[config.GAME_ID_COLUMN].astype(int).tolist())
    print(f"  {len(all_game_ids)} juegos | {len(real_users_df)} usuarios reales")

    genre_features = ev.build_genre_features_df(games_df)
    dist_calc = PairwiseHammingDistanceCalculator(genre_features)

    all_configs = load_all_configs()
    print(f"\nConfigs encontrados: {[c['name'] for c in all_configs]}")

    rows = []
    for cfg in all_configs:
        row = run_single(cfg, games_df, real_users_df, real_prefs_df, all_game_ids, dist_calc)
        rows.append(row)

    sweep_df = pd.DataFrame(rows)
    print_summary(sweep_df)
    _plot_sweep(sweep_df)

    return sweep_df


if __name__ == "__main__":
    run_sweep()
