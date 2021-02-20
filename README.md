## Roadmap

> warmup to revamp yahoo fantasy

- Pinnacle and Bodog data capture using seleniumwire
- sportsipy data capture using library
- since I can't be calling the library and scraping every single day it's better to create a database, use aurora serverless postgres
- try and deploy using AWS chalice
- front-end using React
  - look for an easy template maybe
- serve .csv that crunches numbers for each day
  - get a JS table library that handles this
- try and avoid making a database if possible
  - it might be necessary later if it turns out that it's expensive to make a lot of calls to the NBA API...

## MVP

- Get data from Pinnacle
- function that scrapes Pinnacle each day
- function that get NBA data for each player in Pinnacle list
  - just do current season for now
- function that serves csv each day
- React front-end in S3 bucket

## Summary stats

- avg and std dev
- last 3, 5, 10
- last week, 2 week, month, 3 month
- this season, last season
- last 3 vs team, 5 vs team, 10 vs team

## Database vs API

### Database solution

- get game logs for list of players, update db
- every time encounter new player, get his data for the last 2 seasons, and add him to the list

### API solution

- call API every time, for every player

> Long term DB is better, short term just implement API

### NBA API fork

- using this fork because library does not have all current players (https://github.com/rsforbes/nba_api)
