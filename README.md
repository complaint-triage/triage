## Note Well ##

This software was designed purely to evaluate the application of a large language model
to the problem of triaging complaints. Any information incorporated in or generated by
the software has not been checked for completeness, reliability or accuracy, is not
legal advice, and should not be relied upon as such. Any examples of complaints are
fictitious, and are included for testing and illustration purposes only.

## Licence ##

The software in this repository is licensed under the MIT licence.

The authors are:

* Weisen Huang
* Joey Koh
* Stephen Ma

## Quick Start ##

setup environment:

You'll need python (3.10 has been tested), npm (10.2 is latest stable version), and node (v18.18 is current LTS).

```
git clone git@github.com:complaint-triage/triage.git
cd triage

# create a python virtual environment
python -m venv .venv
. .venv/bin/activate

# install frontend package deps
cd frontend
npm i
cd ..

# install backend package deps
cd backend
pip install -r requirements.txt
cd ..
```

Build the frontend for serving as static files:
```
cd frontend
npm run build
cd ..
```

Azure's OpenAI instances are used for the LLM magic. You'll need to create an Azure
OpenAI resource, and then create a gpt-3.5 deployment (give it the name
`gpt-35-turbo-16k`) and a gpt-4 deployment (named `gpt-4-32k`) in that resource.
This is done in Azure OpenAI studio: https://oai.azure.com/portal/.

You'll also need the endpoint name of the resource and API key for that resource
to access them. Find the endpoint name and key in the Azure portal
(https://portal.azure.com/#view/HubsExtension/BrowseAll - click on the resource
name, then click on "Keys and Endpoint" under the "Resource Management" group in
the left hand side menu.)

The endpoint name is stored in the environment variable `OPENAI_API_BASE` or in
`backend/setting.env`.

The API key is stored in the environment variable `OPENAI_API_KEY` or in
`backend/secret.env`. If the key is misssing when running the backend, you'll
get an error `Did not find openai_api_key`.

Run the backend for local use at `http://localhost:5000`:

```
cd backend
flask run
```

When running flask, the rpc browser is at `http://localhost:5000/t/rpc/browse`

In production you can use gunicorn as the server. The following serves the app at port 8000:

```
cd backend
gunicorn app:app -b :8000 --timeout 300
```
