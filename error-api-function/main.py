from google.oauth2 import service_account
from google.cloud import errorreporting_v1beta1
from google.api_core.client_options import ClientOptions
# import ssl
# context = ssl._create_unverified_context()



# Path to your service account key file
# credentials_path = "/Users/tu.le/Downloads/Highmark_PoC/error-reporting-project-431719-3f117fecf5d1.json"

# Create credentials object
# credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Set client options to use the correct REST endpoint
# Set client options to use the correct REST endpoint
# client_options = ClientOptions(api_endpoint='https://clouderrorreporting.googleapis.com', verify=False)

def list_recent_errors(project_id):
    try:
        # Initialize Error Stats Service Client
        error_stats_client = errorreporting_v1beta1.ErrorStatsServiceClient()

        # project_id = os.environ.get('GCP_PROJECT', 'your-google-cloud-project-id')
        project_name = f"projects/{project_id}"

        # List error group stats
        request = errorreporting_v1beta1.ListGroupStatsRequest(project_name=project_name)
        response = error_stats_client.list_group_stats(request=request)

        for group in response.error_group_stats:
            print(f"Error Group ID: {group.group.group_id}")
            print(f"Error Group Name: {group.group.name}")
            print(f"Total Count: {group.count}")
            print(f"Affected Users Count: {group.affected_users_count}")
            print(f"First Seen: {group.first_seen_time}")
            print(f"Last Seen: {group.last_seen_time}")
            for service in group.affected_services:
                print(f"  Affected Service: {service.service}, Version: {service.version}")
            for count in group.timed_counts:
                print(f"  Timed Count: {count.count}, From: {count.start_time} To: {count.end_time}")
            if group.representative:
                print(f"Representative Event: {group.representative.message}")

                # List error events for the group
                event_request = errorreporting_v1beta1.ListEventsRequest(
                    project_name=project_name,
                    group_id=group.group.group_id
                )
                event_response = error_stats_client.list_events(request=event_request)
                for event in event_response.error_events:
                    print(f"  Error Event: {event.message}, User: {event.context.user}")
                    print(f"  Event Time: {event.event_time}")
                    if event.context.http_request:
                        print(f"  HTTP Method: {event.context.http_request.method}")
                        print(f"  HTTP URL: {event.context.http_request.url}")
                        print(f"  HTTP User Agent: {event.context.http_request.user_agent}")
                        print(f"  HTTP Status Code: {event.context.http_request.response_status_code}")
                    if event.context.report_location:
                        print(f"  File Path: {event.context.report_location.file_path}")
                        print(f"  Line Number: {event.context.report_location.line_number}")
                        print(f"  Function Name: {event.context.report_location.function_name}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    project_id = "[PROJECT_ID]"
    list_recent_errors(project_id)
