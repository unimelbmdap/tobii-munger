from os import PathLike

import polars as pl

__all__ = ["read_unified"]


def _name_generator(ii: int) -> str:
    """Generate column names for the `vals` column in the Tobii data."""
    return "xyz"[ii]


def read_unified(path: PathLike, datatype: str | None = None) -> pl.DataFrame:
    """Read Tobii data from a unified parquet file.

    Arguments:
        path: PathLike
            The path of the unified parquet file to read.
        datatype: str | None, optional
            The datatype to filter the data by. If None, all data is returned.

    Returns:
        pl.DataFrame
            A Polars DataFrame containing the Tobii data from the unified parquet file.
    """
    data = pl.scan_ds(path)
    if datatype is not None:
        data = data.filter(pl.col("type") == datatype)
    return data.with_columns(pl.col("vals").arr.to_struct(name_generator=_name_generator)).unnest("vals").collect()
