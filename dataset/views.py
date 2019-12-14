import os
import math
from time import time
import requests
from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from rest_framework.response import Response
from rest_framework.views import APIView
from core.settings import BING_API_KEY, MONGO_CONNECT, MEDIA_ROOT, MEDIA_URL, DOMAIN


class DataApiView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = MongoClient(MONGO_CONNECT)
        db = self.client.hybrid
        self.dataset: Collection = db.dataset

    def get(self, request, **kwargs):
        name = request.query_params.get("name")
        size = request.query_params.get("size")
        if name is None:
            return Response(status=400)
        if size is None:
            dataset = self.dataset.find({"category": name})
            count = dataset.count()
        else:
            try:
                size = int(size)
            except ValueError:
                return Response(status=400)
            dataset = self.dataset.find({"category": name}).limit(size)
            count = size
        train = []
        test = []
        for index, i in enumerate(dataset):
            data = {"id": str(i["_id"]), "img": DOMAIN + MEDIA_URL + i["img"]}
            if index < count * 0.2:
                test.append(data)
            else:
                train.append(data)
        return Response({"train": train, "test": test})

    def post(self, request):
        list_image = []
        name = request.data.get("name")
        size = request.data.get("size")
        if name is None or size is None:
            return Response(status=400)
        try:
            size = int(size)
        except ValueError:
            return Response(status=400)
        count_api_request = math.ceil(size / 150)
        offset = 0
        with requests.Session() as session:
            url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search/"
            headers = {
                "Ocp-Apim-Subscription-Key": BING_API_KEY,
                "Content-Type": "application/json"
            }
            for _ in range(count_api_request):
                count = 150 if size >= 150 else size
                params = {"q": name, 'count': count, "offset": offset}
                response = session.get(url, params=params, headers=headers).json()
                for i in response["value"]:
                    filename = int(time() * 100)
                    image_path = f"image/{filename}.jpg"
                    try:
                        img = session.get(i["contentUrl"])
                        with open(os.path.join("media", image_path), "wb") as file:
                            file.write(img.content)
                        list_image.append({"category": name, "img": image_path})
                    except requests.exceptions.ConnectionError:
                        continue
                offset = response["nextOffset"]
                size -= count
        self.dataset.insert_many(list_image)
        return Response({"status": "ok"})

    def __del__(self):
        self.client.close()


class DeleteApiView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = MongoClient(MONGO_CONNECT)
        db = self.client.hybrid
        self.dataset: Collection = db.dataset

    def delete(self, request, **kwargs):
        obj = self.dataset.find_one({"_id": ObjectId(kwargs["id"])})
        try:
            os.remove(os.path.join(MEDIA_ROOT, obj["img"]))
            self.dataset.delete_one(obj)
            return Response({"status": "ok", "message": "Image was deleted"})
        except FileNotFoundError:
            return Response({"status": "error"}, status=400)

    def __del__(self):
        self.client.close()
