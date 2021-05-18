## Buy Your Car Chatbot

### To Install Rasa
```
pip install rasa==2.4.0
```

### To train Rasa model
```
rasa train --fixed-model-name "buy-your-car-chatbot"
```

### To start the chatbot in the terminal
```
rasa shell -p 5006
```

### To start Duckling
```
sudo docker run -p 8000:8000 rasa/duckling
```

### To start Rasa Action Server
```
rasa run actions
```
