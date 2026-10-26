import os

import mlflow
import pandas as pd
from pydantic import BaseModel



class InputPatient(BaseModel):
    age: int
    sex: int
    cp : int
    trestbps: int
    chol : int
    fbs : int
    restecg: int
    thalach : int
    exang : int
    oldpeak : float
    slope : int
    ca : int
    thal : int   
    
     
mlflow_uri = os.environ["MLFLOW_TRACKING_URI"]


def test_load_model(model_name, model_version):
    mlflow.set_tracking_uri(mlflow_uri)

    model_uri = f"models:/{model_name}/{model_version}"

    loaded_model = mlflow.pyfunc.load_model(model_uri)
    data = InputPatient(
        age=55,
        sex=1,
        cp=0,
        trestbps=160,
        chol=289,
        fbs=0,
        restecg=0,
        thalach=145,
        exang=1,
        oldpeak=0.8,
        slope=1,
        ca=1,
        thal=3
    )
    columns = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
    # Valores
    features = pd.DataFrame([[
            data.age, data.sex, data.cp, data.trestbps,
            data.chol, data.fbs, data.restecg, data.thalach,
            data.exang, data.oldpeak, data.slope, data.ca, data.thal
        ]], columns=columns)

   
    print(features)

    print("Model loaded:", type(loaded_model))
    print(loaded_model.predict(features))  


def register_best_model(model_name):

    mlflow.set_tracking_uri(mlflow_uri)
    print(mlflow.get_tracking_uri())
    runs = mlflow.search_runs(
        experiment_names=["heart_disease_prediction"],
        order_by=["metrics.f1 DESC"], 
    )

    best_run_id = runs.iloc[0]["run_id"]
    print("Best run ID:", best_run_id)

    
    model_uri = f'runs:/{best_run_id}/model'

    with mlflow.start_run(run_id=best_run_id):
        mlflow.register_model(model_uri=model_uri, name=model_name)




if __name__ == "__main__":  
    model_name = 'heart_disease_prediction'
    register_best_model(model_name)
    test_load_model(model_name, 1)