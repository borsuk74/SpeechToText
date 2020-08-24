from __future__ import division

import re
import sys
#import numpy as np
import grpc
#from google.cloud import speech
#from google.cloud.speech import enums
#from google.cloud.speech import types
import movie_pb2
import movie_pb2_grpc
from concurrent import futures
import random
import time

class FaceServicer(movie_pb2_grpc.FaceServiceServicer):
    def RecognizeFace(self, request, context):

        response = movie_pb2.FaceRecognitionResponse(num=1)
        #response.value = 1
        return response

def serve():
    import os
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/borsuk74/gcp/speechtotext-281122-7d0875e1d1ca.json"
    #print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    movie_pb2_grpc.add_FaceServiceServicer_to_server(FaceServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    try:
        print('Server running on port: 50052')
        serve()
    except KeyboardInterrupt:
        pass