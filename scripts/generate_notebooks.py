"""Generate structured Jupyter notebooks for academic demonstration."""

import json
from pathlib import Path


def create_notebook(title: str, description: str, code_cells: list) -> dict:
    """Construct valid Jupyter notebook structure."""
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"# {title}\n", f"\n{description}\n"]
        }
    ]
    for code in code_cells:
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in code.split("\n")]
        })

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


def main():
    nb_dir = Path("notebooks")
    nb_dir.mkdir(parents=True, exist_ok=True)

    # 01
    nb1 = create_notebook(
        "01 Data Exploration & Ingestion",
        "Explores raw NSE/BSE Bhavcopy datasets and inspects distributions.",
        [
            "import pandas as pd\nimport numpy as np\nfrom pathlib import Path\n\ndf = pd.read_csv('../datasets/sample/synthetic_pump_dump_series.csv')\ndf.head()",
            "df.groupby('symbol').describe()"
        ]
    )
    with open(nb_dir / "01_data_exploration.ipynb", "w") as f:
        json.dump(nb1, f, indent=2)

    # 02
    nb2 = create_notebook(
        "02 Feature Engineering",
        "Calculates price, volume, volatility, and circuit microstructure features.",
        [
            "import sys\nsys.path.append('..')\nimport pandas as pd\nfrom backend.data_pipeline.feature_engineering.feature_builder import build_surveillance_features\n\nraw_df = pd.read_csv('../datasets/sample/synthetic_pump_dump_series.csv')\nfeatured_df, cols = build_surveillance_features(raw_df)\nprint(f'Engineered {len(cols)} features.')\nfeatured_df[cols].head()"
        ]
    )
    with open(nb_dir / "02_feature_engineering.ipynb", "w") as f:
        json.dump(nb2, f, indent=2)

    # 03
    nb3 = create_notebook(
        "03 Isolation Forest Model",
        "Trains unsupervised Isolation Forest for price-volume anomaly detection.",
        [
            "import sys\nsys.path.append('..')\nfrom backend.ml.isolation_forest.train import train_isolation_forest\nfrom backend.ml.isolation_forest.predict import predict_isolation_forest\n\nmodel, normalizer = train_isolation_forest(featured_df, cols)\nscores = predict_isolation_forest(featured_df)\nprint('Mean Isolation Forest score:', scores.mean())"
        ]
    )
    with open(nb_dir / "03_isolation_forest.ipynb", "w") as f:
        json.dump(nb3, f, indent=2)

    # 04
    nb4 = create_notebook(
        "04 PyTorch LSTM Autoencoder",
        "Implements sequence-based LSTM Autoencoder and sequence reconstruction error.",
        [
            "import sys\nsys.path.append('..')\nfrom backend.ml.lstm_autoencoder.train import train_lstm_autoencoder\nfrom backend.ml.lstm_autoencoder.predict import predict_lstm_reconstruction_errors\n\nlstm_model, threshold = train_lstm_autoencoder(featured_df, cols, seq_len=10, epochs=5)\nerrors, meta, thresh = predict_lstm_reconstruction_errors(featured_df)\nprint(f'Calibrated reconstruction threshold: {thresh:.4f}')"
        ]
    )
    with open(nb_dir / "04_lstm_autoencoder.ipynb", "w") as f:
        json.dump(nb4, f, indent=2)

    # 05
    nb5 = create_notebook(
        "05 Model Evaluation & Weak-Label Benchmark",
        "Benchmarks models against SEBI weak ground truth labels.",
        [
            "import sys\nsys.path.append('..')\nfrom backend.app.services.analytics_service import get_model_comparison_benchmark\n\nbenchmarks = get_model_comparison_benchmark()\nimport pandas as pd\npd.DataFrame(benchmarks)"
        ]
    )
    with open(nb_dir / "05_model_evaluation.ipynb", "w") as f:
        json.dump(nb5, f, indent=2)

    print("Generated all 5 demonstration notebooks.")


if __name__ == "__main__":
    main()
