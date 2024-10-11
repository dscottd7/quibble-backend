# quibble-backend
Backend application for Quibble

Responsibilies of the backend: 
- Accepting the (validated by the front end) URLs of the Products that the user wishes to compare
- Making callouts to those URLs to obtain product description information about them from their web pages.  To do this, some “scraping” logic is going to be implemented to extract the “description” or other meaningful information about the product from the product page to pass to OpenAI’s API, as opposed to passing the entire HTML contents of the product web pages, which would be inefficient and potentially overwhelm the API with too much irrelevant information
- Creating the OpenAI assistant (note, this includes specifying which language model we’d like to use - as a stretch goal, we may allow the user to select this, in which case the back end would need to receive the user’s selection from the front end along with the products to compare)
- Creating the OpenAI thread (which includes instructions to compare the two products and the scraped product information, and possibly some specification about the level of detail and formatting of the response requested)
- Executing the OpenAI thread, receiving the response, and passing back to the front end so it can be displayed to the user
- Stretch goal: if implementing logging of a history of product requests, the back end application will need to log each request in a database (SQL, for example) and fetch history information as requested by the front end, if the user navigates to that history display


To do so, will use OpenAI's API, FastAPI, and possibly a tool for web scraping.