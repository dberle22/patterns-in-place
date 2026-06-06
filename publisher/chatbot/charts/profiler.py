"""Profile query results to support deterministic chart selection."""

from __future__ import annotations

from dataclasses import asdict, dataclass

try:
    import pandas as pd
    from pandas.api.types import is_bool_dtype, is_numeric_dtype
except ImportError:  # pragma: no cover - optional dependency in bare environments
    pd = None
    is_bool_dtype = None
    is_numeric_dtype = None


GEO_COLUMNS = {"geo_id", "geo_name", "geo_level", "target_geo_id", "target_geo_level"}
TIME_COLUMNS = {"year", "period", "start_year", "end_year"}
MEASURE_EXCLUDE_COLUMNS = {
    "year",
    "period",
    "rank",
    "highlight_flag",
    "missing_flag",
    "label_flag",
    "display_order",
}


@dataclass
class ResultProfile:
    row_count: int
    has_time_series: bool
    has_geo_column: bool
    dimension_count: int
    measure_count: int
    inferred_shape: str
    time_point_count: int
    geo_column_names: list[str]
    dimension_columns: list[str]
    measure_columns: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ResultProfiler:
    """Inspect a query result frame and infer its chart-relevant shape."""

    def profile(self, dataframe: pd.DataFrame) -> ResultProfile:
        if pd is None:
            raise ImportError("pandas is required to profile query results")

        geo_columns = [column for column in dataframe.columns if column in GEO_COLUMNS]
        time_columns = [column for column in dataframe.columns if column in TIME_COLUMNS]
        measure_columns = [
            column
            for column in dataframe.columns
            if self._is_measure_column(dataframe, column)
        ]
        dimension_columns = [
            column
            for column in dataframe.columns
            if column not in measure_columns and column not in {"metric_id", "metric_label"}
        ]
        time_point_count = self._time_point_count(dataframe, time_columns)
        inferred_shape = self._infer_shape(
            dataframe=dataframe,
            has_geo_column=bool(geo_columns),
            has_time_series=time_point_count > 1,
            measure_columns=measure_columns,
        )

        return ResultProfile(
            row_count=len(dataframe),
            has_time_series=time_point_count > 1,
            has_geo_column=bool(geo_columns),
            dimension_count=len(dimension_columns),
            measure_count=len(measure_columns),
            inferred_shape=inferred_shape,
            time_point_count=time_point_count,
            geo_column_names=geo_columns,
            dimension_columns=dimension_columns,
            measure_columns=measure_columns,
        )

    def _is_measure_column(self, dataframe: pd.DataFrame, column: str) -> bool:
        if column in MEASURE_EXCLUDE_COLUMNS or column in GEO_COLUMNS:
            return False
        series = dataframe[column]
        if is_bool_dtype is not None and is_bool_dtype(series):
            return False
        if is_numeric_dtype is not None and is_numeric_dtype(series):
            return True
        return column in {"metric_value", "benchmark_value", "x_value", "y_value", "size_value"}

    def _time_point_count(self, dataframe: pd.DataFrame, time_columns: list[str]) -> int:
        for column in ("period", "year"):
            if column in dataframe.columns:
                return int(dataframe[column].dropna().nunique())
        if not time_columns:
            return 0
        return int(dataframe[time_columns[0]].dropna().nunique())

    def _infer_shape(
        self,
        *,
        dataframe: pd.DataFrame,
        has_geo_column: bool,
        has_time_series: bool,
        measure_columns: list[str],
    ) -> str:
        if "comparison_group" in dataframe.columns:
            return "benchmark"
        if has_time_series:
            return "trend"
        if {"x_value", "y_value"}.issubset(dataframe.columns) or len(measure_columns) >= 2:
            return "comparison" if has_geo_column and len(dataframe) <= 12 else "correlation"
        if "highlight_flag" in dataframe.columns and len(dataframe) >= 8:
            return "distribution"
        if "rank" in dataframe.columns:
            return "ranking"
        if has_geo_column and len(dataframe) <= 12:
            return "comparison"
        if has_geo_column and len(dataframe) > 12:
            return "distribution"
        return "comparison"
