[![badge](./.github/badges/code_quality.svg)](./code_review/report.json)
[![badge](./.github/badges/total_errors.svg)](./code_review/report.json)

# 🧑‍💻 Food Truck Data, Batch Processing Pipeline

## Pipeline

1. Navigate to the `/pipeline` directory
2. Run `pip3 install requirements.txt`
3. Create a `.env` file and populate it with the following keys:

```
ACCESS_KEY_ID=XXX
SECRET_ACCESS_KEY=XXX
BUCKET_NAME=XXX
DB_HOST=XXX
DB_PORT=XXX
DB_NAME=XXX
DB_USER=XXX
DB_PASSWORD=XXX
DB_SCHEMA=XXX
```

4. Running `pipeline.py` will download and clean the latest batch of data, before loading it into the remote database
5. The Dockerfile can build an image of the pipeline application, suitable for registry in ECR, and subsequent ECS deployment

## Report generation

In this Repository you will find all of the materials for this week of the course.

As well as your coursework files you'll find some additional files

- `README.md`
  - This is the file you are currently reading
- `.gitignore`
  - This file is used to tell Git what files to ignore for any changes. This can be safely ignored.
- `.prettierrc`
  - This file is used to configure Prettier, an automated formatter that we suggest you install. This can be safely ignored.
- `.eslintrc.json` and `pylintrc`
  - Used to ensure that your code is following good style guides
