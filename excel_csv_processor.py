import logging
from pathlib import Path
from typing import Dict, Any

import pandas as pd
from pandas import DataFrame


class ExcelCSVProcessor:
    def __init__(self, file_path: str, encoding: str = 'utf-8', verbose: bool = False):
        self.encoding = encoding
        self.verbose = verbose
        self.file_path = file_path
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        return logger

    def get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        return {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 ** 2,
            'sample_data': df.head(5).to_dict('records')
        }

    def display_preview(self, df: pd.DataFrame, n_rows: int = 5) -> None:
        print(f"data shape: {df.shape}")
        print(f"columns: {list(df.columns)}")
        print(f"data types:\n{df.dtypes}")
        print(f"\nhead {n_rows} row data:")
        print(df.head(n_rows))
        print(f"\ntail {n_rows} row data:")
        print(df.tail(n_rows))

    def read_excel(self, **read_excel_kwargs: None) -> DataFrame | dict[Any, DataFrame] | None:
        file_path = Path(self.file_path)
        if file_path.suffix == '.xlsx':
            excel_df = pd.read_excel(file_path, **read_excel_kwargs)
            self.logger.info(f"Read successfully, {len(excel_df)} row, {len(excel_df.columns)} column")
            return excel_df
        return None

    def read_excel_csv(self, **read_csv_kwargs: None) -> pd.DataFrame:
        file_path = Path(self.file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.logger.info(f"Read the csv file: {file_path}")

        default_kwargs = {
            'encoding': self.encoding,
            'dtype': str,
            'keep_default_na': False,
            'na_values': ['', 'NA', 'N/A', 'null', 'NULL']
        }

        if read_csv_kwargs:
            read_kwargs = {**default_kwargs, **read_csv_kwargs}
        else:
            read_kwargs = default_kwargs

        try:
            df = pd.read_csv(file_path, **read_kwargs)

            df = df.map(lambda x: x[2:-1] if isinstance(x, str) and x.startswith('="') and x.endswith('"') else x)

            self.logger.info(f"Read successfully, {len(df)} row, {len(df.columns)} column")

            return df
        except Exception as e:
            self.logger.error(f"Read failed: {e}")
            raise


if __name__ == "__main__":
    ecp = ExcelCSVProcessor('./data/test.csv', 'utf-8')
    df = ecp.read_excel_csv()
    ecp.display_preview(df)
    ecp.get_summary(df)
    ecp.display_preview(df)
