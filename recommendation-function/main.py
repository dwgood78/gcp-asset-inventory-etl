from google.cloud import recommender_v1
from google.api_core.exceptions import GoogleAPICallError, InvalidArgument
from flask import jsonify

def list_recommendations(request):
    project_id = "error-reporting-432509"
    
    # Replace with the location (e.g., "global", "us-central1")
    location = "global"
    
    # Replace with the recommender ID (e.g., "google.iam.policy.Recommender")
    recommender_id = "google.iam.policy.Recommender"

    client = recommender_v1.RecommenderClient()

    # Construct the parent path
    parent = f"projects/{project_id}/locations/{location}/recommenders/{recommender_id}"

    try:
        # List recommendations
        recommendations = client.list_recommendations(parent=parent)
        recommendations_list = []
        for recommendation in recommendations:
            recommendations_list.append({
                "name": recommendation.name,
                "description": recommendation.description,
                "primary_impact": recommendation.primary_impact.category,
                "recommender_subtype": recommendation.recommender_subtype,
                "state": recommendation.state_info.state
            })
        return jsonify(recommendations_list)

    except InvalidArgument as e:
        print(f"Invalid argument: {e}")
        return f"Error: {str(e)}", 400
    except GoogleAPICallError as e:
        print(f"API call error: {e}")
        return f"Error: {str(e)}", 400
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"Error: {str(e)}", 400
    


