Необходимо прописать в core.settings:  
DOMAIN - адрес сервера  
BING_API_KEY - ключ для доступа к api поиска bing  
MONGO_CONNECT - адрес mongodb

POST /dataset с параметрами name и size осуществляет сбор изображений  
GET /dataset с параметром name позволяет просматривать сохранённые изображения  
DELETE /dataset/id позволяет удалить изображение  
