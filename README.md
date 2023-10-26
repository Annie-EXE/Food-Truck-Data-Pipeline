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
5. The `Dockerfile` can build an image of the pipeline application, suitable for registry in ECR, and subsequent ECS deployment

## Report Generation

1. Navigate to the `/lambda reports` directory
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

4. Running `lambda_function.py` will query the database to calculate key metrics, then use these to populate an HTML report file
5. The `Dockerfile` can build an image of the report generation application, suitable to be deployed with AWS Lambda
