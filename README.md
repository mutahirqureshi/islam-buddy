# Islam Buddy #

Islam Buddy allows you to quickly and conveniently find local Prayer Times and masjid Iqama times.

## Setup ##

Install the required packages.
```
$ pip install -r requirements.txt
```

Install this project's packages and make them findable.
```
$ pip install -e .
```

Run the server
```
$ ./run_server
```

To make a sample request, try:
```
$ ./run_query
```

## API.AI Schema command ##

1. First, obtain your agent's Developer Access Token from API.AI Console
1. Store the token as an environment variable:
   ```
   export DEV_ACCESS_TOKEN='YOUR ACCESS TOKEN'
   ```
1. Run the schema command:
   ```
   $ schema app/assistant.py
   ```
