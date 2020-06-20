import sys
sys.path.append('../../connectTCR')
from connectTCR.io import *
from connectTCR.signal import *

# df = pd.read_csv("../data/timeseries/CSF_TRB.csv")
# t, obs = get_timepoints(df)
# print(t)
# print(obs)
# df[obs].to_csv("../output/timeseries/csf.meta.v3.csv", index=False)

df = pd.read_csv("../data/timeseries/PBMC_TRB_new.csv")
t, obs = get_timepoints(df)
print(t)
print(obs)
print(df.shape)
df[obs].to_csv("../output/timeseries/pb.meta.v2.csv", index=False)