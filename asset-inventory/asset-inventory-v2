import os
import functions_framework
from google.cloud import asset_v1


def asset_inventory_to_bigquery(
    asset_level, asset_level_id, project_id, dataset_name, table_name
):
    """
    Exports asset inventory data to a BigQuery table.
    """
    client = asset_v1.AssetServiceClient()

    # Correct format: "projects/12345" or "folders/67890"
    parent = f"{asset_level}/{asset_level_id}"

    # Note: partition_key must be an ENUM value, not an integer.
    # PARTITION_KEY_UNSPECIFIED = 0, REQUEST_TIME = 1, READ_TIME = 2
    partition_spec = asset_v1.PartitionSpec(
        partition_key=asset_v1.PartitionSpec.PartitionKey.REQUEST_TIME
    )

    # Initialize BigQuery destination
    bigquery_destination = asset_v1.BigQueryDestination(
        dataset=f"projects/{project_id}/datasets/{dataset_name}",
        table=table_name,
        force=False,  # Set to True to overwrite if testing, False to prevent overwrite
        partition_spec=partition_spec,
        separate_tables_per_asset_type=True,
    )

    output_config = asset_v1.OutputConfig(bigquery_destination=bigquery_destination)

    request = asset_v1.ExportAssetsRequest(
        parent=parent,
        content_type=asset_v1.ContentType.RESOURCE,
        output_config=output_config,
    )

    # export_assets returns a Long Running Operation (LRO)
    operation = client.export_assets(request=request)
    operation_name = operation.operation.name
    print(f"Export started: {operation_name}")

    return operation_name


# Entry point for Cloud Function (v2)
@functions_framework.http
def project_details(request):
    # For Cloud Run functions, 'request' is a Flask Request object
    # If triggering via HTTP, you can parse params here or fall back to environment variables.
    request_json = request.get_json(silent=True) or {}

    project_id = request_json.get("project_id") or os.environ.get(
        "BQ_PROJECT_ID", "[PROJECT_ID]"
    )
    dataset_name = request_json.get("dataset_name") or os.environ.get(
        "BQ_DATASET", "demo_asset_inventory"
    )
    table_name = request_json.get("table_name") or os.environ.get(
        "BQ_TABLE", "demo_inventory_v2"
    )  # Tip: Use underscores for BQ tables

    asset_level = request_json.get("asset_level") or os.environ.get(
        "ASSET_LEVEL", "folders"
    )
    asset_level_id = (
        request_json.get("asset_level_id")
        or request_json.get("folder_id")
        or os.environ.get("ASSET_LEVEL_ID", "[FOLDER_ID]")
    )

    try:
        operation_name = asset_inventory_to_bigquery(
            asset_level=asset_level,
            asset_level_id=asset_level_id,
            project_id=project_id,
            dataset_name=dataset_name,
            table_name=table_name,
        )
        return {
            "status": "Inventory export initiated.",
            "operation": operation_name,
        }, 200
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "Export failed", "error": str(e)}, 500
