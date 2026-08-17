# Cloud Function request a connection. VPC Networks are not shown so entered in:
projects/PROJECT_ID/locations/[REGION]/connectors/

projects/PROJECT_ID/locations/[REGION]/connectors/test


# Cloud Pub/Sub trigger events
Cloud Pub/Sub
projects/[PROJECT_ID]/topics/asset-inventory-sub

# Commands to gernerate errors to Error Reporting 

gcloud logging write --payload-type=json test-errors-log \
'{"serviceContext": {"service": "manual-testing"}, "message": "Test Error\n at /test.js:42:42", "context": {"httpRequest": {"url": "/test","method": "GET","responseStatusCode": 500}}}'\

gcloud beta error-reporting events report --service Manual --service-version test1 \
--message "java.lang.TestError: msg at com.example.TestClass.test(TestClass.java:51) at com.example.AnotherClass(AnotherClass.java:25)"
 
## Assest Inventory v2

# set function entry point to "project_details"
gcloud functions deploy asset-inventory-export \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=project_details \
    --trigger-http \
    --no-allow-unauthenticated \
    --timeout=600s \
    --memory=512Mi \
    --service-account="YOUR_SERVICE_ACCOUNT@[PROJECT_ID].iam.gserviceaccount.com"

# Just using IAM method (Preferred)    
# Create BQ dataset
bq mk --location=us-central1 --dataset dcg-cmg-aug-1:demo_asset_inventory

# Grant policy binding
gcloud resource-manager folders add-iam-policy-binding 172636339645 \
    --member="serviceAccount:970013803252-compute@developer.gserviceaccount.com" \
    --role="roles/cloudasset.viewer"

# BigQuery Permissions
gcloud projects add-iam-policy-binding dcg-cmg-aug-1 \
    --member="serviceAccount:970013803252-compute@developer.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding dcg-cmg-aug-1 \
    --member="serviceAccount:970013803252-compute@developer.gserviceaccount.com" \
    --role="roles/bigquery.user"

# Make request 
TOKEN=$(gcloud auth print-identity-token --audiences="https://asset-inventory-v2-970013803252.us-central1.run.app")

curl -X POST "https://asset-inventory-v2-970013803252.us-central1.run.app" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"folder_id": "172636339645"}'

    OR

# IAP Method (Dual or just IAP); make sure bq exists, policy, and permissions applied
1. Open the Google Cloud Console.
2. Make sure project xxxxxxxx-xxx is selected.
3. In the left navigation menu, go to APIs & Services $\rightarrow$ Credentials.Look under the OAuth 2.0 Client IDs table. You will see a Client ID (often named IAP-Secured Web App or created by the system/user). 

It begins with your project number:Plaintext970013803252-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com

4. Copy that entire Client ID string.

# 1. Set the copied Client ID
IAP_CLIENT_ID="970013803252-xxxxxxxxxxxxxxxx.apps.googleusercontent.com"

# 2. Generate identity token with the IAP Client ID
IAP_TOKEN=$(gcloud auth print-identity-token --audiences="${IAP_CLIENT_ID}")

# 3. Call the Cloud Run service
curl -X POST "https://asset-inventory-v2-970013803252.us-central1.run.app" \
    -H "Authorization: Bearer ${IAP_TOKEN}" \
    -H "Content-Type: application/json"