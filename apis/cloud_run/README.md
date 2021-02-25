## Interpreter

- Conda `bbprop_cloud_run`

## Build

- Use `build.sh` script

## Deploy

- local: `docker run --rm -p 8080:8080 -e PORT=8080 bbprop_cloud_run`
- remote: `gcloud beta run deploy bbprop --image gcr.io/bbprop/bbprop_cloud_run --region us-west1 --platform managed`

## Gotchas

- it looks like .gitignore in `cloud_run` directory is being used by gcloud, so don't ignore `docker_env.py` in this file, use `.gitignore` in project root

## Sources

(https://dev.to/googlecloud/using-headless-chrome-with-cloud-run-3fdp)
