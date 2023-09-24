from .scraper import ChatGPTBot
import requests
import json
import subprocess


DB_URL = "https://tailor-mongo-back-end-c176f21f8caf.herokuapp.com/"
CURRENT_DIRECTIONS = "You will be taking in job postings of the form '{{'DESC': a, 'KEYWORDS': b, 'REQUIREMENTS': c}}' and a list of job experiences of the form '[(JOB_TITLE, [DESCRIPTION_1, DESCRIPTION_2, ...]), (JOB_TITLE_2, [DESCRIPTION_1, DESCRIPTION_2], ...),...]'. Once you have received those, you will select the job experiences from the job experiences list that best match the job posting and 2-3 descriptions for each of those experiences that best match the job posting. Then, you will output the selected experiences in a correctly formatted json string of the form 'experience_1: [description_1, description_2], experience_2: [description_1, ...], ...'."


class Resume:
    def __init__(self, user_id: str, job_posting: str) -> None:
        self.user_id = user_id
        self.job_posting = job_posting

    def __getUserData(self) -> dict:
        final_dict = {}
        # GET user_info
        user_info = requests.get(DB_URL + f"user/query?user-id={self.user_id}")
        final_dict["user"] = user_info.json()

        # GET education
        education = requests.get(DB_URL + f"education/query?user-id={self.user_id}")
        final_dict["education"] = education.json()

        # GET experience
        experience = requests.get(DB_URL + f"experience/query?user-id={self.user_id}")
        final_dict["experience"] = experience.json()

        return final_dict

    def __getBestExperience(self, final_dict: dict) -> list:
        experiences = []
        for experience in final_dict["experience"]:
            title = experience["job_title"]
            points = list(experience["bullet_points"].values())
            experiences.append((title, points))

        gpt_bot = ChatGPTBot(CURRENT_DIRECTIONS)
        result = gpt_bot.parse(
            f"job posting: {self.job_posting} \n experiences: {experiences}"
        )

        parsed_suggestion = json.loads(result["choices"][0]["message"]["content"])
        return parsed_suggestion

    def _createJob(self, title, items):
        output_string = f"""
            {{ {title} }}{{ 2022 -- 2023 }}
            {{ {title} }}{{ Iowa City, Iowa}}
            \\resumeItemListStart
        """

        for item in items:
            output_string += f"\n\t\t\\resumeItem{{ {item} }}"

        output_string += "\n\t\\resumeItemListEnd"

        return output_string

    def createResume(self):
        ## SCRAPED

        # final_dict = self.__getUserData()
        # gpt_suggestion = self.__getBestExperience(final_dict)
        # print(gpt_suggestion)

        # # Read the LaTeX template from the file
        # with open("api/modules/static/template.tex", "r") as template_file:
        #     latex_template = template_file.read()

        # first_name = final_dict["user"]["first_name"]
        # last_name = final_dict["user"]["last_name"]
        # city = final_dict["user"]["city"]
        # state = final_dict["user"]["state"]
        # phone_number = final_dict["user"]["phone_number"]
        # resume = (
        #     latex_template.replace("first_name", first_name)
        #     .replace("last_name", last_name)
        #     .replace("city", city)
        #     .replace("state", state)
        #     .replace("phone_number", phone_number)
        #     .replace("university_name", "University of Iowa")
        #     .replace("degree", "MCs in Computer Science")
        # )

        # for i in range(3):
        #     if i >= len(gpt_suggestion):
        #         resume.replace(f"{{job{i}}}", "")
        #     else:
        #         job_title, items = list(gpt_suggestion.items())[i]
        #         resume.replace(f"{{job{i}}}", self._createJob(job_title, items))

        # # Save the filled template to a .tex file
        # with open("resume.tex", "w") as tex_file:
        #     tex_file.write(resume)

        # # Run pdflatex to compile the LaTeX code into a PDF
        # subprocess.run(["pdflatex", "resume.tex"])

        # for the time being just doing this:
        final_dict = self.__getUserData()
        gpt_suggestion = self.__getBestExperience(final_dict)
        return gpt_suggestion


if __name__ == "__main__":
    resume = Resume(
        "650f3a5e13ee8d6494714010",
        "{'DESC': 'Adept is hiring a Software Engineer for their University team in San Francisco, CA. They are focused on building Useful General Intelligence by solving open problems in AI and product development. They have raised significant funding and are backed by strategic partners such as Atlassian, Microsoft, NVIDIA, and Workday. The ideal candidate should have a strong curiosity, communication skills, and problem-solving abilities. They should be willing to learn and have experience in building software systems. Prior experience with neural networks is a plus. The job offers a competitive salary, equity, and benefits packages.', 'KEYWORDS': 'Software Engineer, University, AI, product engineering, neural networks, software systems, Python, Javascript, scalable web applications, CUDA, cloud environments.', 'REQUIREMENTS': 'The requirements for this position include the ability to quickly learn new things, uphold high execution standards, possess excellent communication and presentation skills, and have a degree in Computer Science or a related field. Nice-to-have qualifications include experience with machine learning models, building scalable web applications, managing infrastructure deployments, proficiency in Python and Javascript, writing custom efficient CUDA code, experience with managing a large cluster of computers, and exposure to high-performance networking technologies.'}",
    )
    print(resume.createResume())
