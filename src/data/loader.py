import pandas as pd
import numpy as np
import glob
import os

class Material():
    def __init__(self, path=None):
        self._material_path = path
        self._material = self.load_mat()

    def load_mat(self):
        mat_load = pd.read_csv(self._material_path, header=[0,1,2])
        return mat_load

    @property
    def material(self):
        return self._material


class VNA_Dataloader():
    def __init__(self, path, process=1, fcut=60):
        if process == 1:
            self.experiments = self.process(self.loaddata(path)[0], fcut)
            self.files = self.loaddata(path)[1]
        elif process == 0:
            self.experiments, self.files = self.loaddata(path)
        else:
            print('ERROR: Wrong value encountert')


    def process(self, d, f):
        return np.dstack([d[np.squeeze(np.argwhere(d[:, 0, idx] < f * 10 **6)),:, idx] for idx in range(d.shape[2])])  # omit all values larger than cutoff frequency MHz

    def loaddata(self, p):
        d = []
        for f in self.loadFiles(p):
            exp = np.genfromtxt(f, delimiter=',')
            d.append(np.array(exp))

        d = [d[idx][~np.isnan(d[idx]).all(axis=1), :] for idx, _ in enumerate(d)] # cut first Nan row


        return np.dstack(d), np.array([os.path.basename(f)[:-4] for f in self.loadFiles(p)])

    def loadFiles(self, data_path, fileext=['*.csv', '*.CSV']):
        return np.unique(glob.glob(os.path.join(data_path, '**', fileext[0]), recursive=True) +
                         glob.glob(os.path.join(data_path, '**', fileext[1]), recursive=True))






