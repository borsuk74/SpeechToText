#Primary piece of functionality, which should be wrapped up into
#kivy application. The pyaudio should be replaced with audiostream.
from __future__ import division

import re
import sys
import numpy as np

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue
#import kivy
#import audiostream
import cis
from AuxIVA import AuxIVA
import time
import wave

print(speech.__file__)
# Audio recording parameters
RATE = 16000
#CHUNK = int(RATE / 10)  # 100ms
CHUNK = int(RATE / 1)  # 1000ms


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    #print(len(chunk))
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

    def generator_from_files(self, file_path1, file_path2, chunk_size=8000):
        """
        For testing 2-channel audio translation
        :param file_path1: wav file containing signal from the first microphone
        :param file_path2: wav file containing signal from the second microphone
        :param chunk_size: sequence size used for processing
        :return:y[0] -separated 1st channel, y[1] -2nd channel
        """
        rate1, data1 = cis.wavread(file_path1)
        rate2, data2 = cis.wavread(file_path2)
        #rate1, data1 = cis.wavread('./data/rssd_A.wav')
        #rate2, data2 = cis.wavread('./data/rssd_B.wav')
        if rate1 != rate2:
            raise ValueError('Sampling_rate_Error')
        fs = rate1

        #for ind in range(0, data1.shape[0] - chunk_size, chunk_size):
        for ind in range(0, data1.shape[0] - chunk_size, chunk_size):
            start_time = time.time()
            try:
                x = np.array([data1[ind:ind + chunk_size], data2[ind:ind + chunk_size]], dtype=np.float32)
                y = AuxIVA(x, sample_freq=fs, beta=0.3, nchannel=2).auxiva()
                print("--- %s seconds ---" % (time.time() - start_time))
            except np.linalg.LinAlgError as err:
                if 'Singular matrix' in str(err):
                    # error handling block, probably continue
                    print("Singular matrix")
                    yield np.array([0, 1])
                else:
                    break

            yield y

    def generator_from_file(self, file, chunk=10000):

        f = wave.open(file, "rb")

        data = f.readframes(chunk)
        while len(data) > 0:
            # while data != "":
            # while True:
            yield data
            data = f.readframes(chunk)



def listen_print_loop(responses):
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


def listen_print_loop_multiple(responses):
    """Iterates through server responses and prints them.

   This function will be used when multiple speakers are present in the audio
    """

    num_chars_printed = 0
    for response in responses:

        if not response.results:
            continue

        for result in response.results:
            print("Result is final:"+str(result.is_final))
            print("Channel:"+ str(result.channel_tag))
            # First alternative has words tagged with speakers
            alternative = result.alternatives[0]
            print(u"Transcript: {}".format(alternative.transcript))
            # Print the speaker_tag of each word
            for word in alternative.words:
                print(u"Word: {}".format(word.word))
                print(u"Speaker tag: {}".format(word.speaker_tag))
                print(
                    u"Start time: {} seconds {} nanos".format(
                        word.start_time.seconds, word.start_time.nanos
                    )
                )
                print(
                    u"End time: {} seconds {} nanos".format(
                        word.end_time.seconds, word.end_time.nanos
                    )
                )

def sort_multiple_speakers(responses):

    ret_list = None

    for response in responses:

        if not response.results:
            continue

        for result in response.results:
            if result.is_final:

                ret_list = []
                alternative = result.alternatives[0]
                if alternative is None or len(alternative.words) == 0:
                    continue
                #loop through all words all the time, they are the same, but speaker tags could change
                curr_speaker_tag = alternative.words[0].speaker_tag
                curr_begin_time = int(alternative.words[0].start_time.seconds) + (alternative.words[0].start_time.nanos/1000000000)
                curr_end_time = int(alternative.words[0].end_time.seconds) + (alternative.words[0].end_time.nanos / 1000000000)
                curr_phrase = [alternative.words[0].word]
                ret_list.append((curr_speaker_tag, curr_begin_time,curr_end_time, " ".join(curr_phrase)))
                for word in alternative.words[1:]:
                    if(word.speaker_tag == curr_speaker_tag):
                        # we accumulate the frase for current speaker
                        curr_phrase.append(word.word)
                        # update end_time, begin_time stays the same
                        curr_end_time = int(word.end_time.seconds) + ( word.end_time.nanos / 1000000000)
                        ret_list.pop()
                        ret_list.append((curr_speaker_tag, curr_begin_time, curr_end_time, " ".join(curr_phrase)))
                    else:
                        #we just changed the speaker, append to ret_list the phrase of the previous speaker
                        ret_list.append((curr_speaker_tag, curr_begin_time,curr_end_time, " ".join(curr_phrase)))
                        #initialize everything for new speaker
                        curr_speaker_tag = word.speaker_tag
                        curr_begin_time = int(word.start_time.seconds) + ( word.start_time.nanos / 1000000000)
                        curr_end_time = int(word.end_time.seconds) + (word.end_time.nanos / 1000000000)
                        curr_phrase = [word.word]


                print(ret_list)#for debugging purposes
            #else:
               # print(result.alternatives[0].transcript)

    return ret_list

def sort_multiple_speakers2(responses):

        ret_list = None

        for response in responses:

            if not response.results:
                continue

            for result in response.results:
                if result.is_final:

                    ret_list = []
                    alternative = result.alternatives[0]

                    if alternative is None or len(alternative.words) == 0 or repeat_itself(alternative):
                        continue
                    # loop through all words all the time, they are the same, but speaker tags could change
                    curr_speaker_tag = alternative.words[0].speaker_tag
                    curr_begin_time = int(alternative.words[0].start_time.seconds) + (
                    alternative.words[0].start_time.nanos / 1000000000)
                    curr_end_time = int(alternative.words[0].end_time.seconds) + (
                    alternative.words[0].end_time.nanos / 1000000000)
                    curr_phrase = [alternative.words[0].word]
                    ret_list.append((curr_speaker_tag, curr_begin_time, curr_end_time, " ".join(curr_phrase)))
                    #first_word = alternative.words[0]
                    for word in alternative.words[1:]:
                        #sometimes the same word is repeated twice, I am not sure why ,
                        #so to handle such situation I will skip it
                        #if word == first_word:
                            #continue
                        #else:
                            #first_word = word

                        if (word.speaker_tag == curr_speaker_tag):
                            # we accumulate the frase for current speaker
                            curr_phrase.append(word.word)
                            # update end_time, begin_time stays the same
                            curr_end_time = int(word.end_time.seconds) + (word.end_time.nanos / 1000000000)
                            ret_list.pop()
                            ret_list.append((curr_speaker_tag, curr_begin_time, curr_end_time, " ".join(curr_phrase)))
                        else:
                            # we just changed the speaker, append to ret_list the phrase of the previous speaker
                            ret_list.append((curr_speaker_tag, curr_begin_time, curr_end_time, " ".join(curr_phrase)))
                            # initialize everything for new speaker
                            curr_speaker_tag = word.speaker_tag
                            curr_begin_time = int(word.start_time.seconds) + (word.start_time.nanos / 1000000000)
                            curr_end_time = int(word.end_time.seconds) + (word.end_time.nanos / 1000000000)
                            curr_phrase = [word.word]

                    print(ret_list)  # for debugging purposes
                    # else:
                    # print(result.alternatives[0].transcript)
                else:
                    print(result.alternatives[0].transcript)

        return ret_list


def repeat_itself(altenative):
        '''Sometimes I was getting response with the same words,
         but repeated twice. I don't want to process it'''
        length = len(altenative.words)
        if length % 2 == 1:
            return False
        period = length // 2
        return all([altenative.words[i] == altenative.words[i+period] for i in range(0, period)])





def main():
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/aleks/gcp/speechtotext-281122-7d0875e1d1ca.json"
    print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'en-US'  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        #audio_generator = stream.generator_from_files('./data/rssd_A.wav','./data/rssd_B.wav')
        test_requests = (content for content in audio_generator)

        test_sample = next(test_requests)
        print(type(test_sample))
        print(len(test_sample))
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)

def main_2():
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/aleks/gcp/speechtotext-281122-7d0875e1d1ca.json"
    print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'en-US'  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        #audio_generator = stream.generator()
        audio_generator = stream.generator_from_files('./data/rssd_A.wav','./data/rssd_B.wav')


        #test_requests = (content[0] for content in audio_generator)
        #test_sample = next(test_requests)
        #test_sample = cis.convert_toPyAudio(test_sample)
        #test_sample = test_sample.tostring()
        #print(type(test_sample))
        #print(len(test_sample))

        #print(test_sample.shape)
        requests_0 = (types.StreamingRecognizeRequest(audio_content=cis.convert_toPyAudio(content[0]).tostring())
                    for content in audio_generator)
        #while True:
            #try:
                #next(requests_0)
            #except Exception as err:
                #print("exception"+str(err))
                #break

        responses_0 = client.streaming_recognize(streaming_config, requests_0)

        # Now, put the transcription responses to use.
        listen_print_loop(responses_0)

        audio_generator = stream.generator_from_files('./data/rssd_A.wav', './data/rssd_B.wav')
        requests_1 = (types.StreamingRecognizeRequest(audio_content=cis.convert_toPyAudio(content[1]).tostring())
                      for content in audio_generator )

        responses_1 = client.streaming_recognize(streaming_config, requests_1)

        # Now, put the transcription responses to use.
        listen_print_loop(responses_1)


def main_3():
    '''Experiment to run 2 channels simultaneously. It generates
     "Audio Timeout Error: Long duration elapsed without audio. Audio should be sent close to real time."
     '''
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/aleks/gcp/speechtotext-281122-7d0875e1d1ca.json"
    print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'en-US'  # a BCP-47 language tag

    client0 = speech.SpeechClient()
    client1 = speech.SpeechClient()

    #config = {
        #"audio_channel_count": audio_channel_count,
       # "enable_separate_recognition_per_channel": enable_separate_recognition_per_channel,
       # "language_code": language_code,
    #}

    config = types.RecognitionConfig(
        audio_channel_count=2,
        enable_separate_recognition_per_channel=True,
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        #audio_generator = stream.generator()
        audio_generator0 = stream.generator_from_files('./data/rssd_A.wav','./data/rssd_B.wav')
        audio_generator1 = stream.generator_from_files('./data/rssd_A.wav', './data/rssd_B.wav')

        #test_requests = (content[0] for content in audio_generator)
        #test_sample = next(test_requests)
        #test_sample = cis.convert_toPyAudio(test_sample)
        #test_sample = test_sample.tostring()
        #print(type(test_sample))
        #print(len(test_sample))

        #print(test_sample.shape)
        requests0 = (types.StreamingRecognizeRequest(audio_content=cis.convert_toPyAudio(content[0]).tostring())
                    for content in audio_generator0)
        requests1 = (types.StreamingRecognizeRequest(audio_content=cis.convert_toPyAudio(content[1]).tostring())
                     for content in audio_generator1)


        #while True:
            #try:
                #next(requests_0)
            #except Exception as err:
                #print("exception"+str(err))
                #break

        responses_0 = client0.streaming_recognize(streaming_config, requests0)
        responses_1 = client1.streaming_recognize(streaming_config, requests1)

        # Now, put the transcription responses to use.
        listen_print_loop(responses_0)
        listen_print_loop(responses_1)



def main_4():
    '''Experiment to run 1 channels from mixed file. "
     '''
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/aleks/gcp/speechtotext-281122-7d0875e1d1ca.json"
    print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'en-US'  # a BCP-47 language tag

    client = speech.SpeechClient()

    d_config = types.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=2
    )

    config = types.RecognitionConfig(
        audio_channel_count=2,
        enable_separate_recognition_per_channel=True,
        diarization_config=d_config,
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)

    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        #audio_generator = stream.generator()
        audio_generator = stream.generator_from_file('./data/auxiva2chn.wav')


        #test_requests = (content[0] for content in audio_generator)
        #test_sample = next(test_requests)
        #test_sample = cis.convert_toPyAudio(test_sample)
        #test_sample = test_sample.tostring()
        #print(type(test_sample))
        #print(len(test_sample))

        #print(test_sample.shape)
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)


        #while True:
            #try:
                #next(requests_0)
            #except Exception as err:
                #print("exception"+str(err))
                #break

        response = client.streaming_recognize(streaming_config, requests)

        print(u"Waiting for operation to complete...")


        #for result in response.results:
            # First alternative has words tagged with speakers
            #alternative = result.alternatives[0]
            #print(u"Transcript: {}".format(alternative.transcript))
            # Print the speaker_tag of each word
            #for word in alternative.words:
               # print(u"Word: {}".format(word.word))
               # print(u"Speaker tag: {}".format(word.speaker_tag))

        listen_print_loop(response)



def main_5():
    '''Experiment to run 1 channels from mixed file, which contains multiple
     speakers. We want to test diarization functionality."
     '''
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/aleks/gcp/speechtotext-281122-7d0875e1d1ca.json"
    print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'en-US'  # a BCP-47 language tag

    client = speech.SpeechClient()

    d_config = types.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=2
    )

    config = types.RecognitionConfig(
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
        audio_channel_count=2,
        enable_separate_recognition_per_channel=False,
        model="video",#video, phone_call, command_and_search, or default
        diarization_config=d_config,
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)

    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        #audio_generator = stream.generator()
        #audio_generator = stream.generator_from_file('./data/Bdb001.interaction.wav')
        audio_generator = stream.generator_from_file('./data/2spk_consecutive.wav')


        #test_requests = (content[0] for content in audio_generator)
        #test_sample = next(test_requests)
        #test_sample = cis.convert_toPyAudio(test_sample)
        #test_sample = test_sample.tostring()
        #print(type(test_sample))
        #print(len(test_sample))

        #print(test_sample.shape)
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)




        response = client.streaming_recognize(streaming_config, requests)

        print(u"Waiting for operation to complete...")


        #for result in response.results:
            # First alternative has words tagged with speakers
            #alternative = result.alternatives[0]
            #print(u"Transcript: {}".format(alternative.transcript))
            # Print the speaker_tag of each word
            #for word in alternative.words:
               # print(u"Word: {}".format(word.word))
               # print(u"Speaker tag: {}".format(word.speaker_tag))

        #listen_print_loop_multiple(response)

        ret_list = sort_multiple_speakers2(response)
        print(ret_list)



def main_6():
    '''Experiment to run 1 channels from microphone, which contains multiple
     speakers. I want to test diarization functionality."
     '''
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/aleks/gcp/speechtotext-281122-7d0875e1d1ca.json"
    print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'en-US'  # a BCP-47 language tag

    client = speech.SpeechClient()

    d_config = types.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=2
    )

    config = types.RecognitionConfig(
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
        audio_channel_count=1, #not sure about that, how many channels are in laptop's microphone
        enable_separate_recognition_per_channel=False,
        model="video",
        diarization_config=d_config,
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)

    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        #audio_generator = stream.generator_from_file('./data/2spk_consecutive.wav')


        #test_requests = (content[0] for content in audio_generator)
        #test_sample = next(test_requests)
        #test_sample = cis.convert_toPyAudio(test_sample)
        #test_sample = test_sample.tostring()
        #print(type(test_sample))
        #print(len(test_sample))

        #print(test_sample.shape)
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)




        response = client.streaming_recognize(streaming_config, requests)

        print(u"Waiting for operation to complete...")


        #for result in response.results:
            # First alternative has words tagged with speakers
            #alternative = result.alternatives[0]
            #print(u"Transcript: {}".format(alternative.transcript))
            # Print the speaker_tag of each word
            #for word in alternative.words:
               # print(u"Word: {}".format(word.word))
               # print(u"Speaker tag: {}".format(word.speaker_tag))

        #listen_print_loop_multiple(response)

        ret_list = sort_multiple_speakers(response)
        print(ret_list)



if __name__ == '__main__':
    main_5()