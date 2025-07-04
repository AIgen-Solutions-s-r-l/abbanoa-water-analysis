"""BigQuery configuration and connection management."""

from dataclasses import dataclass
from typing import Optional

from google.cloud import bigquery
from google.oauth2 import service_account


@dataclass
class BigQueryConfig:
    """Configuration for BigQuery connection."""

    project_id: str
    dataset_id: str
    credentials_path: Optional[str] = None
    location: str = "EU"

    @property
    def dataset_ref(self) -> str:
        """Get full dataset reference."""
        return f"{self.project_id}.{self.dataset_id}"


class BigQueryConnection:
    """Manages BigQuery client connection."""

    def __init__(self, config: BigQueryConfig) -> None:
        self.config = config
        self._client: Optional[bigquery.Client] = None

    @property
    def client(self) -> bigquery.Client:
        """Get or create BigQuery client."""
        if self._client is None:
            # Check if credentials_path points to Application Default Credentials
            if (
                self.config.credentials_path
                and "application_default_credentials.json"
                in self.config.credentials_path
            ):
                # Use default credentials for ADC
                self._client = bigquery.Client(project=self.config.project_id)
            elif self.config.credentials_path:
                # Use service account credentials
                try:
                    credentials = service_account.Credentials.from_service_account_file(
                        self.config.credentials_path
                    )
                    self._client = bigquery.Client(
                        credentials=credentials, project=self.config.project_id
                    )
                except Exception:
                    # Fall back to default credentials if service account fails
                    self._client = bigquery.Client(project=self.config.project_id)
            else:
                # Use default credentials
                self._client = bigquery.Client(project=self.config.project_id)

        return self._client

    def get_dataset(self) -> bigquery.Dataset:
        """Get dataset reference."""
        return self.client.dataset(self.config.dataset_id)

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the dataset."""
        table_ref = f"{self.config.dataset_ref}.{table_name}"
        try:
            self.client.get_table(table_ref)
            return True
        except Exception:
            return False
