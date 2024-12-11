## Deployment to Google Cloud Platform
1) Setup Google Cloud Platform
    - Create a Project
    - Activate Cloud Run Api and Cloud Build API
    - And at least you have access to Cloud Run 
2) Setup Google Cloud SDK
    - You can follow the instructions here [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install) to installation
    - Init your google cloud project in Google Cloud SDK
3) Create Dockerfile, requirements.txt, main.py
4) Cloud Build and Deploy
    ```
    docker build -t my-flask-app:v1.0 .

    gcloud artifacts repositories create api-stunting --repository-format=docker --location=asia-southeast2

    docker tag my-flask-app:v1.0 asia-southeast2-docker.pkg.dev/stuntrack-capstonefinal/api-stunting/my-flask-app:v1.0

    docker push asia-southeast2-docker.pkg.dev/stuntrack-capstonefinal/api-stunting/my-flask-app:v1.0
    
    ```
4) Testing with Postman to /predict
    {
      "umur": 50,
      "jenis_kelamin": 1,
      "tinggi_badan": 90
    }  

## License
This project is licensed by C242-PS376 Team Bangkit Cohort 2024 Batch 2.
