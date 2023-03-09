import logging
import os
import pickle
import pandas as pd
import numpy as np
from heapq import nlargest
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import azure.functions as func


try:
    logging.info("Azure Blob Storage v" + __version__)
    conn_str = os.getenv("oc_blob_conn_str")
    container_name = "p9-storage"
    

    blob_clicks = BlobClient.from_connection_string(
        conn_str = conn_str,
        container_name = container_name,
        blob_name = "df_clicks_azure.pkl"
    )
    clicks = pickle.loads(blob_clicks.download_blob().readall())
    
    blob_emb = BlobClient.from_connection_string(
        conn_str = conn_str,
        container_name = container_name,
        blob_name = "df_art_env_pca.pkl"
    )
    embedding = pickle.loads(blob_emb.download_blob().readall())
    
    blob_model = BlobClient.from_connection_string(
        conn_str = conn_str,
        container_name = container_name,
        # blob_name = "NMF_model"
        blob_name = "_model_NMF.pickle"
    )
    model = pickle.loads(blob_model.download_blob().readall())
    model = model["algo"]
    

except Exception as e:
    print("EXCEPTION : ")
    print(e)

# fonction pour obtenir les recommandations par collaborative filtering
def get_recommandation_cf(user_id, embedding, clicks, algo, n=5):

    idx=list(embedding.index)

    clicked = clicks[
        clicks["user_id"] == user_id
    ]["click_article_id"].tolist()
    for item in clicked:
        if item in idx:
            idx.remove(item)
    res = {}
    for i in idx:
        pred = algo.predict(user_id, i)
        res[pred.iid]=pred.est
    return nlargest(n, res, key=res.get)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Reception requete HTTP")
    
    user_id = req.params.get("user_id")
    if(isinstance(user_id, str)):
        user_id = int(user_id)
    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_id = req_body.get("user_id")
    
    if user_id:
        rec = get_recommandation_cf(user_id, embedding, clicks, model)
        return func.HttpResponse(str(rec), status_code=200)
    else:
        logging.info(":( Diantre! Il y a eu une erreur !")
        return func.HttpResponse(
            ":( Requête invalide",
            status_code=400
        )
