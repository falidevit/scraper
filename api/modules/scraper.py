import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import logging
import os
import openai

CURRENT_DIRECTIONS = 'You are a tool that takes in a string that consists of all the visible text in a web page and determines if the web page is a job posting. If it is not a job posting, then you return the string "ERROR: Not a job posting." If it is a job posting, you return a string in the form "(!)DESC: a; (!)KEYWORDS: b <<>> x (!)REQUIREMENTS: c", where a is a 50-word summary of the job description, b is the job\'s keywords and technologies, and c is the job\'s requirements. Make sure to include the (!) symbols in the response.'


class ChatGPTBot:
    def __init__(self, system_directions: str) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.system_message = {"role": "system", "content": system_directions}

    def parse(self, user_message: str):
        # openai.api_key = os.getenv("CHAT_GPT_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                self.system_message,
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0.2,
            max_tokens=1500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return response


class Scraper:
    """Class for all job posting scraper logic."""

    ERROR_STRING = ""

    def __init__(self) -> None:
        pass

    def _processHTML(self, html: str) -> str:
        """_summary_

        Args:
            html (str): _description_

        Returns:
            str: _description_
        """
        beautiful_html = BeautifulSoup(html, "html.parser")
        all_page_text = beautiful_html.find_all(text=True)

        # Iterate through text and get all visible text
        visible_text = []
        for text_element in all_page_text:
            if text_element.parent.name in [
                "style",
                "script",
                "head",
                "title",
                "meta",
                "[document]",
            ] or isinstance(text_element, Comment):
                continue
            visible_text.append(text_element)

        output_string = " ".join([string.strip() for string in visible_text])
        return output_string

    def _makeDictionary(self, gpt_response: str) -> dict:
        response_items = gpt_response.split("(!)")
        response_dict = {}

        for item in response_items[1:]:
            key, description = item.split(":", maxsplit=1)
            response_dict[key] = description.strip()

        return response_dict

    def scrape(self, url: str) -> str:
        """Scrapes the given job posting URL and outputs a string in the form:
        'DESC: description; KEYWORDS: keywords; REQUIREMENTS: requirements'. Outputs error string if URL does
        not lead to job posting.

        Args:
            url (str): URL to a job description

        Returns:
            str: string in the form:
        'DESC: description; KEYWORDS: keywords; REQUIREMENTS: requirements' or ''
        """
        url_request = requests.get(url)
        if url_request.status_code != 200:
            logging.error("REQUEST ERROR: Could not query given site.")
            return Scraper.ERROR_STRING

        # Process string
        raw_html = url_request.text
        processed_string = self._processHTML(raw_html)

        # Create GPT instance
        gpt_instance = ChatGPTBot(CURRENT_DIRECTIONS)
        gpt_response = gpt_instance.parse(processed_string)
        gpt_processed_string = gpt_response["choices"][0]["message"]["content"]

        # Create output dictionary
        if gpt_processed_string != "ERROR: Not a job posting.":
            output = self._makeDictionary(gpt_processed_string)
        else:
            logging.error(f"ERROR: Not a job posting \n {gpt_processed_string}")
            output = {}
        return output


if __name__ == "__main__":
    new_scraper = Scraper()
    job_url = "https://boards.greenhouse.io/adept/jobs/4265377006"
    print(new_scraper.scrape(job_url))
