# import the Flask class from the flask module
from flask import Flask, request
from flask import jsonify
import api.modules.scraper as scraper
from urllib.parse import quote, unquote

# create the application object
app = Flask(__name__)


@app.route("/scrape", methods=["GET"])
def home():
    args = request.args.to_dict()
    decoded_url = unquote(args["url"])

    url_scraper = scraper.Scraper()
    output_dict = url_scraper.scrape(decoded_url)

    return jsonify(output_dict)  # return a string


# start the server with the 'run()' method
if __name__ == "__main__":
    app.run(debug=True)
