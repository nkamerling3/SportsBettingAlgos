import numpy as np
import DTLearner as dt
import LinRegLearner as lrl


class DTLearner(object):

    def __init__(self, DT, LinReg, verbose=False):
        """
        Constructor method
        """
        self.dt = DT
        self.lrl = LinReg
        self.verbose = verbose

    def query(self, points):
        pred_y_dt = self.dt.query(points)
        pred_y_linreg = self.lrl.query(points)
        if self.verbose:
            print("dt prediction:")
            print(pred_y_dt)
            print("lin reg prediction")
            print(pred_y_linreg)
        return (pred_y_dt + pred_y_linreg) / 2
