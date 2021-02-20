## Build and run Docker container

- Build the container - run from `bbprop-data` directory, because Docker can't use external folders and I need to include `bbprop` module
  `docker build -t bbprop_cloud_run -f bbprop_api/cloud_run/Dockerfile .`
- Run the container:
  `docker run --rm -p 8080:8080 -e PORT=8080 bbprop_cloud_run`

## Deployment

- Build step - also run this from `bbprop-data` directory
  `gcloud builds submit --tag gcr.io/bbprop/bbprop_cloud_run`
- Run:
  `gcloud beta run deploy bbprop --image gcr.io/bbprop/bbprop_cloud_run --region us-west1 --platform managed`

## Roadmap

- implement in docker first
-
- Pinnacle scraper must be in cloud run container
- then output dataframe to bucket

  - use lambda, with API gateway

- figure out how to schedule it

- another function that will request the csv, for Next.js

## Not Yet

- lambda /cloud function for updating game logs every day

- then cloud run will need to have access to game log csvs
  - either google bucket solution or lambda function with API gateway

## Sources

(https://dev.to/googlecloud/using-headless-chrome-with-cloud-run-3fdp)
