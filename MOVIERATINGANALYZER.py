# movie_rating_analyzer.py
"""
Movie Rating Analyzer
---------------------
Reads a movies.csv file, cleans it, analyzes ratings,
creates charts, and exports summary CSVs.

Run:  python movie_rating_analyzer.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


# ---------- Config ----------
DATA_PATH = "movies.csv"   # Input dataset
OK = "ok"                  # Folder to save results


# ---------- Helpers ----------
def ensure_dataset(path: str):
    """Create a sample movies.csv if one doesn't already exist."""
    if os.path.exists(path):
        return
    
    sample = [
        ("Inception", "Sci-Fi", 8.8, 2010),
        ("Titanic", "Romance, Drama", 7.8, 1997),
        ("Interstellar", "Sci-Fi, Drama", 8.6, 2014),
        ("The Dark Knight", "Action, Crime", 9.0, 2008),
        ("Avengers: Endgame", "Action, Superhero", 8.4, 2019),
        ("La La Land", "Romance, Musical", 8.0, 2016),
        ("Parasite", "Thriller, Drama", 8.6, 2019),
        ("Mad Max: Fury Road", "Action, Adventure", 8.1, 2015),
        ("The Godfather", "Crime, Drama", 9.2, 1972),
        ("Toy Story 3", "Animation, Family", 8.3, 2010),
        ("Whiplash", "Drama, Music", 8.5, 2014),
        ("Coco", "Animation, Family", 8.4, 2017),
        ("Dangal", "Drama, Sport", 8.4, 2016),
        ("3 Idiots", "Comedy, Drama", 8.4, 2009),
        ("Joker", "Crime, Drama", 8.5, 2019),
        ("The Shawshank Redemption", "Drama", 9.3, 1994),
        ("Forrest Gump", "Drama, Romance", 8.8, 1994),
        ("RRR", "Action, Drama", 8.0, 2022),
        ("K.G.F: Chapter 2", "Action, Crime", 8.2, 2022),
        ("The Avengers", "Action, Superhero", 8.0, 2012),
    ]
    df = pd.DataFrame(sample, columns=["Title", "Genre", "Rating", "Year"])
    df.to_csv(path, index=False)


def load_and_clean(path: str) -> pd.DataFrame:
    """Load movies csv and clean types and formatting."""
    df = pd.read_csv(path)
    df.columns = [c.strip().title() for c in df.columns]
    keep = [c for c in ["Title", "Genre", "Rating", "Year"] if c in df.columns]
    df = df[keep].copy()
    
    for c in ["Title", "Genre"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    
    if "Rating" in df.columns:
        df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    
    df = df.dropna(subset=["Title", "Genre", "Rating", "Year"])
    df["Rating"] = df["Rating"].clip(0, 10)
    return df


def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    """Split comma-separated genres into rows for aggregation."""
    tmp = df.copy()
    tmp["Genre"] = tmp["Genre"].astype(str).str.split(",")  # ✅ fixed here
    tmp = tmp.explode("Genre")
    tmp["Genre"] = tmp["Genre"].str.strip()
    tmp = tmp[tmp["Genre"] != ""]
    return tmp


def chart_avg_rating_by_genre(exp: pd.DataFrame, out_path: str):
    genre_avg = (
        exp.groupby("Genre", as_index=False)["Rating"]
        .mean()
        .sort_values("Rating", ascending=False)
    )
    plt.figure(figsize=(10, 6))
    plt.bar(genre_avg["Genre"], genre_avg["Rating"])
    plt.title("Average Rating by Genre")
    plt.xlabel("Genre")
    plt.ylabel("Average Rating")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    return genre_avg


def chart_movies_per_year(df: pd.DataFrame, out_path: str):
    per_year = df.groupby("Year").size().reset_index(name="Count").sort_values("Year")
    plt.figure(figsize=(10, 6))
    plt.bar(per_year["Year"].astype(str), per_year["Count"])
    plt.title("Movies Released Per Year")
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    return per_year


# ---------- Main ----------
def main():
    os.makedirs(OK, exist_ok=True)

    ensure_dataset(DATA_PATH)
    df_clean = load_and_clean(DATA_PATH)
    df_exploded = explode_genres(df_clean)

    top5 = df_clean.sort_values("Rating", ascending=False).head(5)[["Title", "Rating", "Year"]]

    genre_avg = chart_avg_rating_by_genre(df_exploded, os.path.join(OK, "avg_rating_by_genre.png"))
    per_year = chart_movies_per_year(df_clean, os.path.join(OK, "movies_per_year.png"))

    # Save CSVs
    df_clean.to_csv(os.path.join(OK, "Details_movies.csv"), index=False)
    genre_avg.to_csv(os.path.join(OK, "genre_avg_ratings.csv"), index=False)
    top5.to_csv(os.path.join(OK, "top5_movies.csv"), index=False)
    per_year.to_csv(os.path.join(OK, "movies_per_year.csv"), index=False)

    print("✅ UNDERSTOOD! Outputs in:", OK)


if __name__ == "__main__":
    main()
