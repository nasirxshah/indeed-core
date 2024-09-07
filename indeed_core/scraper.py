from indeed_core.session import Session
from bs4 import BeautifulSoup
import re
import json
from indeed_core.models import JobModel
from indeed_core.exceptions import JobParseError, ValidationError
import pydantic
import datetime as dt
from io import StringIO

class Indeed:
    def __init__(self, base_url, proxy: str | None = None) -> None:
        self.base_url = base_url
        self.session = Session(proxy=proxy)

    def jobsearch(self, keyword=None, location=None, radius=None, date_posted=None, remote=None, start=None, pp=None):
        """
        remote: 0kf:attr(DSQF7);|0kf:attr(PAXZC);
        date_posted: 1|3|7|14
        radius: 0|5|10|15|25|35|50|100
        """
        params = {}
        if keyword:
            params["q"] = keyword

        if location:
            params["l"] = location

        if radius:
            params["radius"] = radius

        if date_posted:
            params["fromage"] = date_posted
        
        if remote == "remote":
            params['sc'] = "0kf:attr(DSQF7);"
            
        if remote == "hybrid":
            params['sc'] = "|0kf:attr(PAXZC);"
        
        if start:
            params['start'] = start
            assert pp is not None
            params['pp'] = pp


        if not params:
            raise ValueError(
                "The parameters dict is empty. Please provide at least one parameter."
            )

        response_text = self.session.request(
            "GET", f"{self.base_url}/jobs", params=params
        )
        return self.jobparse(response_text), self.next_pp(response_text, start)

    def next_pp(self, response_text, start):
        next = start + 10 if start else 10
        matched = re.search(r'"pageLinks":\s*(?P<page_links>\[.*?\])', response_text, re.DOTALL)
        if matched:
            page_links_str = matched.groupdict()['page_links']            
            page_links = json.loads(page_links_str)
            for page_link in page_links:
                if f"start={next}" in page_link['href']:
                    next_pp = page_link['pp']
                    return next_pp
                

    def jobparse(self, response_text):
        soup = BeautifulSoup(response_text, features="lxml")

        mosaic_data_script = soup.find("script", id="mosaic-data")
        
        jobcards_pattern = re.compile(
            r"window\.mosaic\.providerData\[\"mosaic-provider-jobcards\"\]\s?=\s?(?P<mosaic_data>{.*?});",
            re.DOTALL,
        )

        matched = jobcards_pattern.search(mosaic_data_script.text)
        if not matched:
            raise JobParseError("could'nt find mosaic data, probably indeed structure is changed")
        
        mosaic_data_str = matched.groupdict()["mosaic_data"]

        mosaic_data = json.loads(mosaic_data_str)


        job_cards = mosaic_data.get('metaData', {}).get('mosaicProviderJobCardsModel', {}).get('results', [])
        
        if mosaic_data and not job_cards:
            raise JobParseError("could'nt find job cards from mosaic data, probably json structure is changed")
        
        cards = []
        for job_card in job_cards:
            card = {
                'job_id': job_card.get("jobkey"),
                'job_title': job_card.get("title"),
                'job_city': job_card.get("jobLocationCity"),
                'job_state': job_card.get("jobLocationState"),
                'job_link': self.base_url + job_card.get("viewJobLink"),
                'published_date': dt.datetime.fromtimestamp(job_card.get("pubDate")/1000),
                'job_types': job_card.get("jobTypes"),
                "salary_max": job_card.get("extractedSalary", {}).get("max"),
                "salary_min": job_card.get("extractedSalary", {}).get("min"),
                "salary_type": job_card.get("extractedSalary", {}).get("type"),
                "salary_currency": job_card.get("salarySnippet", {}).get("currency"),
                "employer_name": job_card.get("company"),
                "employer_rating": job_card.get("companyRating"),
                "employer_review_count": job_card.get("companyReviewCount")
            }

            snippet = job_card.get("snippet")
            if snippet:
                soup = BeautifulSoup(StringIO(snippet), features="lxml")
                card['job_description'] = soup.text.strip()

            cards.append(card)

        self.validate(cards, JobModel)
        return cards


    def validate(self, jobs, model):
        errors = []
        for job in jobs:
            try:
                model(**job)
            except pydantic.ValidationError as e:
                errors.extend(e.errors())

        if errors:
            raise ValidationError(errors)
