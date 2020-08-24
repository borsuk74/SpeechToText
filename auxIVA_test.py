import numpy as np
import cis
from AuxIVA import AuxIVA
import time


rate1, data1 = cis.wavread('./data/rssd_A.wav')
rate2, data2 = cis.wavread('./data/rssd_B.wav')
#rate3, data3 = cis.wavread('./samples/mixdata/mix3.wav')
if rate1 != rate2 :#or rate2 != rate3:
    raise ValueError('Sampling_rate_Error')
fs = rate1
print(fs)
print(data1.shape)


start_time = time.time()

x = np.array([data1[:10000], data2[:10000]], dtype=np.float32)
y = AuxIVA(x, sample_freq=fs, beta=0.3,nchannel=2).auxiva()

print("--- %s seconds ---" % (time.time() - start_time))