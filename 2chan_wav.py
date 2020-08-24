#generate and write 2 channels

import wave, struct, math

def generate_2chnls():
    sampleRate = 44100.0 # hertz
    duration = 1.0       # seconds

    # Use different frequencies for the left and right channels
    rFreq = 1760.00  # A
    lFreq =  523.25  # C

    wavef = wave.open('sound.wav','w')
    wavef.setnchannels(2) # stereo
    wavef.setsampwidth(2)
    wavef.setframerate(sampleRate)

    for i in range(int(duration * sampleRate)):
        l = int(32767.0*math.cos(lFreq*math.pi*float(i)/float(sampleRate)))
        r = int(32767.0*math.cos(rFreq*math.pi*float(i)/float(sampleRate)))
        wavef.writeframesraw( struct.pack('<hh', l, r ) )

    wavef.writeframes('')
    wavef.close()

def combine_two_channals(file1,file2, outfile):
    '''read inputs from two wav files and insert into third one.
    This one do it correctly'''

    f1 = wave.open(file1, "rb")
    f2 = wave.open(file2, "rb")

    wavef = wave.open(outfile, 'w')
    wavef.setnchannels(2)  # stereo
    wavef.setsampwidth(2)  #2bytes per datapoint
    wavef.setframerate(f1.getframerate())

    data1 = f1.readframes(1)
    data2 = f2.readframes(1)
    while len(data1) > 0:

            wavef.writeframesraw( data1+ data2)
            data1 = f1.readframes(1)
            data2 = f2.readframes(1)

    wavef.writeframes('')
    wavef.close()



#The wave module returns the frames as a string of bytes, which can be converted to numbers with the struct module. For instance:

def oneChannel(fname, chanIdx):
    """ list with specified channel's data from multichannel wave with 16-bit data """
    f = wave.open(fname, 'rb')
    chans = f.getnchannels()
    samps = f.getnframes()
    sampwidth = f.getsampwidth()
    assert sampwidth == 2
    s = f.readframes(samps) #read the all the samples from the file into a byte string
    f.close()
    unpstr = '<{0}h'.format(samps*chans) #little-endian 16-bit samples
    x = list(struct.unpack(unpstr, s)) #convert the byte string into a list of ints
    return x[chanIdx::chans] #return the desired channel


def combine_2into_1(file1,file2, outfile):
    """This one is wrong!"""
    import wave

    infiles = [file1, file2]

    data = []
    for infile in infiles:
        w = wave.open(infile, 'rb')
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()

    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    output.writeframes(data[0][1])
    output.writeframes(data[1][1])
    output.close()

def comb_2into_1(file1,file2, outfile):
    """This one is wrong too!"""
    import wave

    infiles = [file1, file2]

    with wave.open(outfile, 'wb') as wav_out:
        for wav_path in infiles:
            with wave.open(wav_path, 'rb') as wav_in:
                if not wav_out.getnframes():
                    wav_out.setparams(wav_in.getparams())
                wav_out.writeframes(wav_in.readframes(wav_in.getnframes()))




chan0 = oneChannel('./data/pzm12a.wav',0)

combine_two_channals("./data/auxiva_1.wav", "./data/auxiva_2.wav", "./data/auxiva2chn.wav")


print("Hello")