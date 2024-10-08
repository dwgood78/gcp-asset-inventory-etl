# Pull the image from GHCR to your local machine using
docker pull <not-reachable-location> .

# Tag the image for GCR: (Replace `[PROJECT_ID]` with your actual GCP project ID).
docker tag <not-reachable-location> gcr.io/error-reporting-432509/<nameofimage> 

# Push the image to GCR:
docker push gcr.io/error-reporting-432509/<nameofimage>


docker pull ghcr.io/chaos-mesh/chaos-mesh:v2.6.3
docker pull ghcr.io/chaos-mesh/chaos-daemon:v2.6.3
docker pull ghcr.io/chaos-mesh/chaos-dashboard:v2.6.3
docker pull ghcr.io/chaos-mesh/chaos-coredns:v0.2.6
 
docker tag ghcr.io/chaos-mesh/chaos-mesh:v2.6.3 gcr.io/error-reporting-432509/chaos-mesh:v2.6.3
docker tag ghcr.io/chaos-mesh/chaos-daemon:v2.6.3 gcr.io/error-reporting-432509/chaos-daemon:v2.6.3
docker tag ghcr.io/chaos-mesh/chaos-dashboard:v2.6.3 gcr.io/error-reporting-432509/chaos-dashboard:v2.6.3
docker tag ghcr.io/chaos-mesh/chaos-coredns:v0.2.6 gcr.io/error-reporting-432509/chaos-coredns:v0.2.6

docker push gcr.io/error-reporting-432509/chaos-mesh:v2.6.3
docker push gcr.io/error-reporting-432509/chaos-daemon:v2.6.3
docker push gcr.io/error-reporting-432509/chaos-dashboard:v2.6.3
docker push gcr.io/error-reporting-432509/chaos-coredns:v0.2.6