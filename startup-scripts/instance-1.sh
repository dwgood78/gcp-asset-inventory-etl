#!/bin/bash

# Install required dependencies
sudo apt-get update
sudo apt-get install google-cloud-sdk

# Initialize the gcloud SDK
gcloud init

# Configure the project
gcloud config set project starry-diode-376414

# Set the default zone
gcloud config set compute/zone us-central1-c

# Create a service account with the Error Reporting Admin role
gcloud iam service-accounts create error-reporting-service-account --display-name="Error Reporting Service Account"

# Grant the service account the Error Reporting Admin role
gcloud iam service-accounts add-role roles/logging.logWriter error-reporting-service-account

# Create a key for the service account
gcloud iam service-accounts keys create error-reporting-service-account.json --iam-account=error-reporting-service-account@starry-diode-376414.iam.gserviceaccount.com

# Set the service account credentials
gcloud auth activate-service-account --key-file error-reporting-service-account.json

# Write all logged events to Error Reporting
gcloud logging write-entries --resource-type=global --resource-labels=service=my-service --log-name=my-log --entries-file=/var/log/syslog