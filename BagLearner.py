import numpy as np
import LinRegLearner as lrl
import DTLearner as dt
import RTLearner as rt


class BagLearner(object):
    """
    This is a Bag Learner

    :param verbose: If “verbose” is True, your code can print out information for debugging.
        If verbose = False your code should not generate ANY output. When we test your code, verbose will be False.
    :type verbose: bool
    """

    def __init__(self, learner, kwargs, bags, boost=False, verbose=False):
        """
        Constructor method
        """
        self.learners = []
        for i in range(bags):
            self.learners.append(learner(**kwargs))
        self.bags = bags
        self.boost = boost
        self.verbose = verbose
        self.bag_query_list = []

    def author(self):
        """
        :return: The GT username of the student
        :rtype: str
        """
        return "nkamerling3"

    def add_evidence(self, data_x, data_y):
        data_subsets = []
        #generate unique subsets of data
        for i in range(self.bags):
            random_bag_rows = np.random.choice(data_x.shape[0], data_x.shape[0], replace=True)
            # random_bag_data_x = data_x[random_bag_rows]
            while self._subset_already_exists(data_subsets, random_bag_rows):
                random_bag_rows = np.random.choice(data_x.shape[0], data_x.shape[0], replace=True)
            data_subsets.append(sorted(random_bag_rows))

        for i in range(self.bags):
            random_bag_data_x = data_x[data_subsets[i]]
            # if self.verbose:
                # print("x data passed in:")
                # print(random_bag_data_x)
                # print(f"length: {len(random_bag_data_x)}")
            random_bag_data_y = data_y[data_subsets[i]]
            # if self.verbose:
                # print("y data passed in:")
                # print(random_bag_data_y)
                # print(f"length: {len(random_bag_data_y)}")
            self.learners[i].add_evidence(random_bag_data_x, random_bag_data_y)

    def _subset_already_exists(self, data_subsets, random_bag_rows):
        if len(data_subsets) <= 1:
            return False
        else:
            for i in range(len(data_subsets)):
                if sorted(random_bag_rows) == data_subsets[i]:
                    if self.verbose:
                        print("Same subset detected")
                        print("current subset")
                        print(sorted(random_bag_rows))
                        print("data subset")
                        print(data_subsets[i])
                    return True

    def query(self, points, make_list=False):  # make_list set to true if looking at only one point
        cumulative_y = np.zeros(points.shape[0])
        cumulative_value = 0
        for i in range(self.bags):
            pred_y_points = self.learners[i].query(points)
            if make_list:
                self.bag_query_list.append(pred_y_points[0])
            if self.verbose:
                nan_mask = np.isnan(pred_y_points)
                nan_indices = np.argwhere(nan_mask)
                if len(nan_indices) > 0:
                    print("nan values are at index:")
                    print(nan_indices)
                    print(f"bag number is: {i}")
                    print("points causing issue")
                    print(points[nan_indices])
            cumulative_y += pred_y_points

        pred_y = cumulative_y/self.bags

        return pred_y


    def get_bag_query_list(self):
        return self.bag_query_list
