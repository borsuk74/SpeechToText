from __future__ import division

import re
import sys
import numpy as np
import grpc
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from concurrent import futures
import random
import time

class SpeechStreamingService(types.cloud_speech_pb2_grpc.SpeechServicer):

    def __init__(self):

        super().__init__()
        self._speech_client = speech.SpeechClient()
        self._is_first_message = True


    def StreamingRecognize(self, request_iterator, context):

        print("Recieved streaming request")

        # We need to capture a configuration from the first incoming request,
        # which corresponds to call of StartRecognizing on the client side. All other requests
        # will have  configuration  empty.
        if(self._is_first_message == True):
            request = next(request_iterator)
            if( request.streaming_config.interim_results == True):

                self._is_first_message = False
                self._streaming_config = request.streaming_config;


        #Here we can inject custom logic to modify audio content
        requests = (types.StreamingRecognizeRequest(audio_content=request.audio_content)
                    for request in request_iterator)

        responses = self._speech_client.streaming_recognize(self._streaming_config, requests)



        # Now, print the transcription responses to use,
        # self._listen_print_loop(responses)

        #but actually we need to yield them

        for response in responses:
            yield response

        self._is_first_message = True



    def _listen_print_loop(self, responses):
        """Iterates through server responses and prints them.

        The responses passed is a generator that will block until a response
        is provided by the server.

        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.

        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since once it's `is_final`, it
            # moves on to considering the next utterance.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                print(transcript + overwrite_chars)

                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r'\b(exit|quit)\b', transcript, re.I):
                    print('Exiting..')
                    break

                num_chars_printed = 0
'''
    def StreamingRecognize(self, request_iterator, context):

        print("Recieved streaming request")

        for request in request_iterator:
            # yield types.cloud_speech_pb2.StreamingRecognizeResponse()
            print(type(request.audio_content))
            if (len(request.audio_content) > 0):
                print(len(request.audio_content))
                print("Audio counter: ", self._audio_counter)
                self._audio_counter += 1
                if (self._audio_counter == 1):
                    print("Audio counter is zero")
                    print(request.audio_content)
            if (request.streaming_config.interim_results == True):
                print(request.streaming_config)
                print(type(request.streaming_config.config))
                print("Config counter:", self._config_counter)
                self._config_counter += 1
'''

'''
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

'''
def serve():
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/borsuk74/gcp/speechtotext-281122-7d0875e1d1ca.json"
    #print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    types.cloud_speech_pb2_grpc.add_SpeechServicer_to_server(SpeechStreamingService(),server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    try:
        print('Server running on port: 50051')
        serve()
    except KeyboardInterrupt:
        pass