import torch
from matplotlib import pyplot as plt
import numpy as np
import cv2
import pandas
import os
import pygame
import base64
import requests
import json
import openai

model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5/runs/train/exp__/weights/best.pt', force_reload=True)

pygame.mixer.init()
def playsound(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

with open('key.txt', 'r') as file: api_key = file.read()
with open('prompt.txt', 'r') as file: prompt = file.read()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def sus(image_path):
    base64_image = encode_image(image_path)

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }

    payload = {
      "model": "gpt-4o",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": prompt
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    message = response.json()['choices'][0]['message']['content']
    
    if message == 'Yes': return True
    elif message == 'No': return False
    else: return None

def faceid():    
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        results = model(frame)
        cv2.imshow('YOLO', np.squeeze(results.render()))

        if cv2.waitKey(10) & 0xFF == ord('q'):
            print("Locked.")
            playsound("womp.mp3")
            out = False
            break
        
        if len(results.xyxy[0]) != 0:
            if (results.xyxy[0][0][-1] == 15).item():
                if (results.xyxy[0][0][4] > 0.9).item():
                    cv2.imwrite("frame.jpg", frame)
                    if sus("frame.jpg"):
                        print("Unlocked!")
                        playsound("partyhorn.mp3")
                        out = True
                    else:
                        print("Cheater!")
                        playsound("womp.mp3")
                        out = False
                    os.remove("frame.jpg")
                    break
    
    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    
    return out

faceid()
