# Cloud Function request a connection. VPC Networks are not shown so entered in:
projects/PROJECT_ID/locations/us-central1/connectors/

projects/PROJECT_ID/locations/us-central1/connectors/test


# Cloud Pub/Sub trigger events
Cloud Pub/Sub
projects/starry-diode-376414/topics/asset-inventory-sub

# Commands to gernerate errors to Error Reporting 

gcloud logging write --payload-type=json test-errors-log \
'{"serviceContext": {"service": "manual-testing"}, "message": "Test Error\n at /test.js:42:42", "context": {"httpRequest": {"url": "/test","method": "GET","responseStatusCode": 500}}}'\

gcloud beta error-reporting events report --service Manual --service-version test1 \
--message "java.lang.TestError: msg at com.example.TestClass.test(TestClass.java:51) at com.example.AnotherClass(AnotherClass.java:25)"
 