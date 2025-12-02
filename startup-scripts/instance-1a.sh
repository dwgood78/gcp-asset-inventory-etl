#!/bin/bash

# Enable Error Reporting
gcloud logging settings enable-error-reporting

# Assign the Error Reporting Admin role to the instance's service account
gcloud compute instances add-metadata --metadata XXXXXX-compute@developer.gserviceaccount.com=roles/logging.logWriter NAMEOFINSTANCE

# Enable Cloud Logging for the instance
gcloud compute instances add-metadata --metadata google-logging-enabled=true NAMEOFINSTANCE