import json
import requests
import os
import flask
from datetime import datetime, timedelta

from flask import render_template, request, jsonify
from urllib.parse import parse_qs, urlencode

from canonicalwebteam.flask_base.app import FlaskBase
from canonicalwebteam.templatefinder import TemplateFinder
from canonicalwebteam import image_template

app = FlaskBase(
    __name__,
    "documentationacademy.org",
    template_folder="../templates",
    static_folder="../static",
)

session = requests.Session()


@app.context_processor
def global_template_context():
    # Fetch live GitHub issues (cached for 30 minutes)
    github_issues = fetch_github_issues()

    return {
        "latest_issues": github_issues,
        "path": flask.request.path,
    }


@app.errorhandler(Exception)
def render_error_page(error):
    app.logger.error(
        f"Error occurred: {error}",
        exc_info=os.environ.get("DISPLAY_FULL_TRACEBACK").lower() == "true",
    )
    error_code = getattr(error, "code", 500)
    error_message = getattr(error, "description", "Something went wrong!")
    return render_template(
        "error.html", error_code=int(error_code), error_message=error_message
    )


template_finder_view = TemplateFinder.as_view("template_finder")
app.add_url_rule("/", view_func=template_finder_view)
app.add_url_rule("/<path:subpath>", view_func=template_finder_view)


def modify_query(params):
    query_params = parse_qs(
        request.query_string.decode("utf-8"), keep_blank_values=True
    )
    query_params.update(params)

    return urlencode(query_params, doseq=True)


@app.context_processor
def utility_processor():
    return {
        "modify_query": modify_query,
        "image": image_template,
    }


# Cache for GitHub issues
issues_cache = {"data": None, "timestamp": None}

CACHE_DURATION = timedelta(minutes=30)


def fetch_github_issues():
    """
    Fetch the latest 5 GitHub issues from canonical/open-documentation-academy.
    Results are cached for 30 minutes.
    Returns the formatted issues list or None on error.
    """
    global issues_cache

    # Check if cache is valid
    now = datetime.now()
    if (
        issues_cache["data"] is not None
        and issues_cache["timestamp"] is not None
        and now - issues_cache["timestamp"] < CACHE_DURATION
    ):
        return issues_cache["data"]

    # Fetch fresh data from GitHub API
    try:
        github_url = "https://api.github.com/repos/canonical/open-documentation-academy/issues"
        params = {
            "state": "open",
            "sort": "created",
            "direction": "desc",
            "per_page": 15,
            "pulls": "false",
        }

        response = session.get(github_url, params=params, timeout=10)
        response.raise_for_status()

        issues_data = response.json()

        # Filter out pull requests (PRs have a 'pull_request' key)
        issues_only = [
            issue for issue in issues_data if "pull_request" not in issue
        ]

        # Format the response
        formatted_issues = [
            {
                "number": issue["number"],
                "title": issue["title"],
                "url": issue["html_url"],
                "state": issue["state"],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "user": {
                    "login": issue["user"]["login"],
                    "avatar_url": issue["user"]["avatar_url"],
                    "url": issue["user"]["html_url"],
                },
                "labels": [label["name"] for label in issue.get("labels", [])],
                "comments": issue.get("comments", 0),
            }
            for issue in issues_only[
                :5
            ]  # Ensure we only get 5 issues after filtering
        ]

        # Update cache
        issues_cache["data"] = formatted_issues
        issues_cache["timestamp"] = now

        return formatted_issues

    except requests.RequestException as e:
        app.logger.error(f"Failed to fetch GitHub issues: {e}")

        # If cache exists, return stale data
        if issues_cache["data"] is not None:
            return issues_cache["data"]

        # Otherwise return None
        return None


@app.route("/api/latest-issues")
def get_latest_issues():
    """
    API endpoint to fetch the latest 5 GitHub issues.
    """
    issues = fetch_github_issues()

    if issues is not None:
        return jsonify(issues)
    else:
        return jsonify({"error": "Failed to fetch issues from GitHub"}), 503
