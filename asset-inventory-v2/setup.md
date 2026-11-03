## Setup
# create function, run from folder

gcloud functions deploy asset-inventory-v3 \
    --gen2 \
    --runtime=python312 \
    --region=us-east4 \
    --source=asset-inventory \
    --entry-point=project_details \
    --trigger-http \
    --no-allow-unauthenticated \
    --set-env-vars="BQ_PROJECT_ID=PROJECT_ID,ASSET_LEVEL_ID=FOLDER_ID"

# Add supporting Cloud Run function

export PROJECT_ID="xxxxxxxxx"
export REGION="us-east4"
export DATASET_ID="iam_audit_dataset"
export TABLE_PREFIX="artifact_registry_iam_analysis"
export FUNCTION_NAME="export-ar-iam-analysis"
export RUN_SA="crf-iam-analyzer@${PROJECT_ID}.iam.gserviceaccount.com"
export SCHEDULER_SA="scheduler-iam-trigger@${PROJECT_ID}.iam.gserviceaccount.com"

# Enable Cloud Asset, Cloud Run, Cloud Build, Cloud Scheduler, and Artifact Registry APIs

gcloud services enable \
    cloudasset.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    cloudscheduler.googleapis.com \
    artifactregistry.googleapis.com \
    bigquery.googleapis.com \
    --project="${PROJECT_ID}"

# create bq

bq --location="${REGION}" mk \
    --project_id="${PROJECT_ID}" \
    --dataset "${PROJECT_ID}:${DATASET_ID}"

# create sa and iam roles
# Service account for Cloud Run Function

gcloud iam service-accounts create crf-iam-analyzer \
    --display-name="Cloud Run Function IAM Policy Analyzer" \
    --project="${PROJECT_ID}"

# Service account for Cloud Scheduler

gcloud iam service-accounts create scheduler-iam-trigger \
    --display-name="Cloud Scheduler Trigger" \
    --project="${PROJECT_ID}"

# grant perms for cloud run function sa

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${RUN_SA}" \
    --role="roles/cloudasset.viewer"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${RUN_SA}" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${RUN_SA}" \
    --role="roles/bigquery.jobUser"

# write function 
# requirements.txt

functions-framework==3.*
google-cloud-asset>=3.10.0

# main.py

import os
import functions_framework
from google.cloud import asset_v1

@functions_framework.http
def run_iam_export(request):
    project_id = os.environ.get("PROJECT_ID")
    dataset_id = os.environ.get("DATASET_ID")
    table_prefix = os.environ.get("TABLE_PREFIX", "ar_iam_analysis")

    client = asset_v1.AssetServiceClient()
    parent = f"projects/{project_id}"

    # Target Artifact Registry repositories and evaluate permissions
    analysis_query = asset_v1.IamPolicyAnalysisQuery(
        scope=parent,
        resource_selector=asset_v1.IamPolicyAnalysisQuery.ResourceSelector(
            full_resource_name=f"//artifactregistry.googleapis.com/projects/{project_id}"
        ),
        options=asset_v1.IamPolicyAnalysisQuery.Options(
            expand_groups=True,
            expand_roles=True,
            output_resource_edges=True
        )
    )

    output_config = asset_v1.IamPolicyAnalysisOutputConfig(
        bigquery_destination=asset_v1.IamPolicyAnalysisOutputConfig.BigQueryDestination(
            dataset=f"projects/{project_id}/datasets/{dataset_id}",
            table_prefix=table_prefix,
            write_disposition="WRITE_APPEND"
        )
    )

    request_payload = asset_v1.ExportIamPolicyAnalysisRequest(
        analysis_query=analysis_query,
        output_config=output_config
    )

    # Start long-running export operation
    operation = client.export_iam_policy_analysis(request=request_payload)
    return f"Export operation triggered: {operation.operation.name}", 200

# deploy 

gcloud functions deploy "${FUNCTION_NAME}" \
    --gen2 \
    --runtime=python311 \
    --region="${REGION}" \
    --source=. \
    --entry-point=run_iam_export \
    --trigger-http \
    --no-allow-unauthenticated \
    --service-account="${RUN_SA}" \
    --set-env-vars PROJECT_ID="${PROJECT_ID}",DATASET_ID="${DATASET_ID}",TABLE_PREFIX="${TABLE_PREFIX}" \
    --project="${PROJECT_ID}"

# retrieve function 

export FUNCTION_URL=$(gcloud functions describe "${FUNCTION_NAME}" \
    --gen2 \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --format="value(serviceConfig.uri)")

# create scheduler job
# grant perms

gcloud run services add-iam-policy-binding "${FUNCTION_NAME}" \
    --region="${REGION}" \
    --member="serviceAccount:${SCHEDULER_SA}" \
    --role="roles/run.invoker" \
    --project="${PROJECT_ID}"

# create scheduler job

gcloud scheduler jobs create http ar-iam-export-weekly \
    --location="${REGION}" \
    --schedule="30 9,14 * * *" \    
    --time-zone="Etc/UTC" \
    --uri="${FUNCTION_URL}" \
    --http-method=POST \
    --oidc-service-account-email="${SCHEDULER_SA}" \
    --oidc-token-audience="${FUNCTION_URL}" \
    --project="${PROJECT_ID}"

# review binding in bq

SELECT
  analysis_query.resource_selector.full_resource_name AS target_resource,
  iam_binding.role AS assigned_role,
  member AS principal_identity
FROM
  `${PROJECT_ID}.iam_audit_dataset.artifact_registry_iam_analysis_*`,
  UNNEST(analysis_results) AS result,
  UNNEST(result.iam_binding.members) AS member
WHERE
  iam_binding.role LIKE '%artifactregistry%'
GROUP BY 1, 2, 3
ORDER BY principal_identity;