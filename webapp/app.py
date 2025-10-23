import requests
import os
import flask
import yaml

from flask import render_template, request
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
    return {
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
