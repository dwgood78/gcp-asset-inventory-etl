import os
import functions_framework
from google.cloud import asset_v1
from google.api_core.exceptions import GoogleAPICallError

@functions_framework.http
def run_iam_export(request):
    try:
        project_id = os.environ.get("PROJECT_ID", "dcg-cmg-nov-1")
        dataset_id = os.environ.get("DATASET_ID", "iam_audit_dataset")
        table_prefix = os.environ.get("TABLE_PREFIX", "artifact_registry_iam_analysis")

        client = asset_v1.AssetServiceClient()
        parent = f"projects/{project_id}"

        # Target Artifact Registry permissions across project scope
        analysis_query = {
            "scope": parent,
            "access_selector": {
                "roles": [
                    "roles/artifactregistry.admin",
                    "roles/artifactregistry.repoAdmin",
                    "roles/artifactregistry.writer",
                    "roles/artifactregistry.reader"
                ]
            },
            "options": {
                "expand_groups": True,
                "expand_roles": True,
                "output_resource_edges": True
            }
        }

        output_config = {
            "bigquery_destination": {
                "dataset": f"projects/{project_id}/datasets/{dataset_id}",
                "table_prefix": table_prefix,
                "write_disposition": "WRITE_APPEND"
            }
        }

        # Trigger the long-running export operation
        operation = client.export_iam_policy_analysis(
            request={
                "analysis_query": analysis_query,
                "output_config": output_config
            }
        )

        return (f"Export operation initiated: {operation.operation.name}", 200)

    except GoogleAPICallError as e:
        print(f"Google API Error: {e.message}")
        return (f"API Error: {e.message}", 500)
    except Exception as e:
        print(f"Unhandled Exception: {str(e)}")
        return (f"Internal Error: {str(e)}", 500)