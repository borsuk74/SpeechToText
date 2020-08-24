from __future__ import division

import re
import sys
#import numpy as np
import grpc
#from google.cloud import speech
#from google.cloud.speech import enums
#from google.cloud.speech import types
import face_pb2
import face_pb2_grpc
from concurrent import futures
import random
import time
from PIL import Image

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TKAgg', force=True)


class FaceServicer(face_pb2_grpc.FaceServiceServicer):
    def RecognizeFace(self, request, context):
        print("We got request!")
        timeStamp = request.timeStamp
        if len(request.videoContent) > 0:
            print(type(request.videoContent))
            images = list(request.videoContent)
            image = Image.frombytes('RGBA', (160, 160), images[0])
            print("We got some image here!")
            #image.show()
            plt.title(str(timeStamp))
            plt.imshow(image)
            plt.show()
            plt.clf()
            image.close()

        response = face_pb2.FaceRecognitionResponse(num=1)
        #response.value = 1
        return response

def serve():
    import os
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/borsuk74/gcp/speechtotext-281122-7d0875e1d1ca.json"
    #print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    face_pb2_grpc.add_FaceServiceServicer_to_server(FaceServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    try:
        print('Server running on port: 50052')
        serve()
    except KeyboardInterrupt:
        pass