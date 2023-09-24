# import the Flask class from the flask module
from flask import Flask, request
from flask import jsonify
import api.modules.scraper as scraper
import api.modules.resume as resume
from urllib.parse import quote, unquote

# create the application object
app = Flask(__name__)


@app.route("/scrape", methods=["GET"])
def scrape():
    args = request.args.to_dict()
    decoded_url = unquote(args["url"])
    user_id = args["user-id"]

    url_scraper = scraper.Scraper()
    output_dict = url_scraper.scrape(decoded_url)

    my_resume = resume.Resume(user_id, str(output_dict))
    gpt_suggestion = my_resume.createResume()

    return jsonify(gpt_suggestion)  # return a string


# start the server with the 'run()' method
if __name__ == "__main__":
    app.run()
