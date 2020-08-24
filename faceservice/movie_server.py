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



class MovieService(movie_pb2_grpc.MovieServiceServicer):

    def MovieChat(self, request_iterator, context):
        print("Recieved streaming request")
        #prev_movies = []
        #for new_movie in request_iterator:
            #for prev_movie in prev_movies:
                #if prev_movie.movie_id == new_movie.movie_id:
                    #yield movie_pb2.MovieNote(prev_movie.movie_id,
                                              #random.randint(1, 5))
            #prev_movies.append(new_movie)
        for new_movie in request_iterator:
            print(new_movie.title)
            #if new_movie.title == "Movie 6":
                #raise Exception("Error for number 6")
            #else:
            time.sleep(1.0)
            yield movie_pb2.MovieNote(movie_id=new_movie.title,
                                      movie_rating=random.randint(1, 5))
            #time.sleep(1.0)


    def AddMovie(self, request, context):
        print('Received request')
        # logic to perform request
        movie_id = 'from python'

        return movie_pb2.AddMovieResponse(movie_id=movie_id)

def serve():
    import os
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/borsuk74/gcp/speechtotext-281122-7d0875e1d1ca.json"
    #print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    movie_pb2_grpc.add_MovieServiceServicer_to_server(MovieService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    try:
        print('Server running on port: 50051')
        serve()
    except KeyboardInterrupt:
        pass