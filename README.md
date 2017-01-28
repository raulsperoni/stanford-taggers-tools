# Stanford taggers tools
Side, incomplete project built for a grade Thesis at:
Facultad de Ingeniería - Udelar
Raúl Speroni - Martín Steglich

## Installation and execution

1. Install [Docker](https://docs.docker.com/installation/).

2. Build an image from Dockerfile:

```bash
git clone
docker-compose up
```

## What is this

We developed these tools as a side project for our grade thesis. The aim was to interact more easily with both Staford NER and Stanford POS taggers. We were also interested in training our own spanish model for Tweets, and for that we had to build a tool for the anotation of a new Corpus.
This is not a finished project, we encourage you to use and modify it under your own responsability.


### Tweet downloader
It downloads tweets using Twitter API, you can set credentials in libs/config.py and search criteria using ENV variables. Tweets are stored in a Mongo database also in a Docker container.

### Training Server
Exposes via Flask some services to anotate tweets with NER tags with the objective of building your own corpus.
Service is Authenticated, but you can create new users with a PIN that you can set as an ENV variable.

### Training WEB
A simple AngularJS web for anotating Tweets and save them through the Training Server.
You can see an example:

The tags we defined are:

*LUG: Places
*PER: People
*ORG: Organizations
*OTRA: Other entities


### Jupyter
Python Jupyter allows to interact with the rest of the modules and scripts built for this project. It is useful for generating the tabulated file from the corpus for training new Stanford models. 

### NER y POS server
It allows you via Rest services to:

*Choose between Stanford models and Languages.
*Load a new corpus and train the model.
*Get POS tags for a text.
*Get NER tags for a text.

See some examples below:

#### Usage as a simple Server
When running as a simple server, both NER and POS Stanford servers will be started and will listen for querys.
Note you need to change docker-compose.yml to run stanford_server.py directly. In this mode models should be inside "stanford" folder and proper enviroment variables should be set in docker-compose.yml file.

Here is an invocation example:
```python
import ner
class Stanford():
    """
    Clase que se conecta al servidor NER Stanford y devuelve el texto anotado.
    """

    def __init__(self, ner_host='localhost', ner_port=9191, ner_output_format='inlineXML',pos_port=9190):
        if ner_output_format not in ('slashTags', 'xml', 'inlineXML'):
            raise ValueError('Formato de salida %s invalido.' % ner_output_format)
        self.ner_tagger = ner.SocketNER(host=ner_host,port=ner_port)
        self.pos_tagger = ner.SocketNER(host=ner_host,port=pos_port)
        
    def tag(self,text):
        """
        Retorna texto anotado
        """
        return self.ner_tagger.tag_text(text)
    
    def pos(self,text):
        """
        Retorna texto anotado
        """
        return self.pos_tagger.tag_text(text)
```
#### Usage through a Restful API
By default docker will start a Restful API wich you can use to start and stop both NER and POS servers. This API also allows you to train new Stanford models transfering training data from a client. You can print each operation results using:
```python
print response.content
```
#### Transfer .tsv file
```python
import requests
url = 'http://172.17.0.2:5000/ner/train'
files = {'file': open('prueba_train.tsv')}
response = requests.post(url, files=files)
```
#### Train new model
```python
import requests
url = 'http://172.17.0.2:5000/ner/train'
response = requests.get(url)
```
#### List available models
```python
import requests
url = 'http://172.17.0.2:5000/ner/models'
response = requests.get(url)
```
#### Start NER server
```python
import requests
url = 'http://172.17.0.2:5000/ner/start'
response = requests.get(url)
```
#### Stop NER server
```python
import requests
url = 'http://172.17.0.2:5000/ner/stop'
response = requests.get(url)
```
#### Check NER server status
```python
import requests
url = 'http://172.17.0.2:5000/ner/status'
response = requests.get(url)
```
#### Start POS server
```python
import requests
url = 'http://172.17.0.2:5000/pos/start'
response = requests.get(url)
```
#### Stop POS server
```python
import requests
url = 'http://172.17.0.2:5000/pos/stop'
response = requests.get(url)
```
#### Check POS server status
```python
import requests
url = 'http://172.17.0.2:5000/pos/status'
response = requests.get(url)
```
