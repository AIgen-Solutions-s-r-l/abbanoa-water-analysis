"""
BigQuery client wrapper for the water infrastructure system.
"""

import os
from typing import Optional

from google.cloud import bigquery
from google.oauth2 import service_account


class BigQueryClient:
    """Wrapper for BigQuery client with project configuration."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """Initialize BigQuery client."""
        self.project_id = project_id or os.getenv(
            "BIGQUERY_PROJECT_ID", "abbanoa-464816"
        )
        self.dataset_id = dataset_id or os.getenv(
            "BIGQUERY_DATASET_ID", "water_infrastructure"
        )
        self.location = location or os.getenv("BIGQUERY_LOCATION", "EU")

        # Initialize client
        self.client = self._create_client()

    def _create_client(self) -> Optional[bigquery.Client]:
        """Create BigQuery client with proper authentication."""
        # Check for service account credentials
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if (
            credentials_path
            and os.path.exists(credentials_path)
            and os.path.getsize(credentials_path) > 0
        ):
            try:
                print(f"Loading service account credentials from: {credentials_path}")
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                client = bigquery.Client(
                    project=self.project_id,
                    credentials=credentials,
                    location=self.location,
                )
                print(
                    f"BigQuery client created successfully with project: {self.project_id}"
                )
                return client
            except Exception as e:
                print(f"Failed to load service account credentials: {e}")
                print(f"Error type: {type(e).__name__}")
                return None
        else:
            try:
                # Use application default credentials
                print("Attempting to use application default credentials...")
                client = bigquery.Client(
                    project=self.project_id, location=self.location
                )
                print(
                    f"BigQuery client created successfully with project: {self.project_id}"
                )
                return client
            except Exception as e:
                print(f"Failed to create BigQuery client with default credentials: {e}")
                print(f"Error type: {type(e).__name__}")
                return None

    def get_dataset_reference(self) -> bigquery.DatasetReference:
        """Get dataset reference."""
        return self.client.dataset(self.dataset_id)

    def get_table_reference(self, table_name: str) -> bigquery.TableReference:
        """Get table reference."""
        dataset_ref = self.get_dataset_reference()
        return dataset_ref.table(table_name)
