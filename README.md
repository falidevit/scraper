# Job Scraper and Resume Suggestion API
This repo contains the code for our job scraping and AI resume suggestion service. We built it using the OpenAI API. The API has only one action:

```
GET https://tailor-job-scraper-7e4b7f88930e.herokuapp.com/scrape?url=<JOB-URL>&user-id=<USERID>
```

Which takes in a user ID corresponding to a user in the MongoDB database and a URL to a job posting. The response to the request is then a list the AI matched job experiences from the user's profile that are best suited for the job posting.
