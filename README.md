## Steps to understand this code challenge solution
1. Read challenge-description.pdf
2. Read this README
3. Dive into the code, wools_scraping_orchestrator.py is a good starting point

<br>

## Solution discussion
### Design and Development Considerations
- I have assumed the logical scope of this challenge is only the backend. 

- To facilitate design discussion and later make iterations over it, I would have designed UML diagrams such as class or component diagrams before beginning the coding phase.

- The backend utilizes web scraping techniques  employing the requests and bs4 modules (since loading a browser is expensive) to extract data from the selected websites. To enhance performance and accuracy, web scraping is carried out utilizing the website's native browser, leveraging their optimized search algorithms. However, it is necessary to implement additional logic to verify that the located product corresponds to the desired one, as information on web pages can occasionally be unreliable.

- If the code or data format of a web page changes, exceptions will occur in the corresponding website scraper, alerting developers that adaptation is required. The parsing process for the remaining websites will continue as usual.

- For this challenge, to store the data I will use an easy to read self-descriptive JSON file: 

```json
{
   "wools":[
      {
         "brand":"Drops",
         "model":"Safran",
         "offeredInPlatforms":[
            {
               "platform":"Wollplatz",
               "info":{
                  "price":10,
                  "composition":"cotton",
                  ...
               }
            }
         ]
      }
   ]
}
```


- The code has been tested with Python 3.10


### Future considerations

- The scraper classes can be further divided into separate Crawler and Parser classes if more complex web scraping is required.
- Taking advantage of the microservices architecture, a FastAPI or Flask API could be developed for the backend, following REST principles, with the following endpoints:
    - POST /wools:  Adds a new wool product. Given a list of websites and a list of woll balls' search info (in this case brand and model), it scrapes (crawling and parsing included) and stores in the backend the available data, 
    - GET /wools : Returns a list of all wools available

    If required by website requirements, additional endpoints could be added, e.g. GET /wools/{brand}/{model}, DELETE /wools/{brand}/{model}
    
- A database engine like PostgreSQL or MongoDB could be added. In this case I would choose a non-relational database as it is more scalable, shorter in development time, more flexible to data model changes, and as the web scraping nature leads to data inconsistency.

- This future whole architecture could also be interpreted as a MVC architecture, being the backend the Model and Controller.

- I would have added pytest unit and integration tests, though I think it's already sufficient to make a decision at this stage of the interview process

### Tools
- PyCharm with IdeaVim plugin.
- Python Virtual Environments.
- I strive to adhere to clean code principles such as SOLID Principles, KISS, YAGNI, The Zen of Python, and Software Design Principles.
- I would use a linter and include it as a phase in the CI pipeline.
- I would utilize logging and leverage the advanced features of the built-in logging library.
- I would adhere to the conventional commits specification.
