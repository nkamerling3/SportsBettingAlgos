import numpy as np


class DTLearner(object):
    """
    This is a Decision Tree Learner

    :param verbose: If “verbose” is True, your code can print out information for debugging.
        If verbose = False your code should not generate ANY output. When we test your code, verbose will be False.
    :type verbose: bool
    """

    def __init__(self, leaf_size, verbose=False):
        """
        Constructor method
        """
        self.tree = None
        self.leaf_size = leaf_size
        self.verbose = verbose
        if self.verbose:
            print(self.leaf_size)

    def author(self):
        """
        :return: The GT username of the student
        :rtype: str
        """
        return "nkamerling3"

    def add_evidence(self, data_x, data_y):
        #clear_existing tree
        self.tree = np.array([])
        self.tree = self._build_tree(data_x, data_y)
        if self.verbose:
            print(self.tree)

    def query(self, points):
        pred_y = np.array([])
        for point in points:
            pred_y_point = self._query_point(0, point)
            pred_y = np.append(pred_y, pred_y_point)
        return pred_y

    def _query_point(self, row, point):
        if self.tree[row][0] == -1:
            return self.tree[row][1]
        else:
            best_column = self.tree[row][0]
            column_value = point[int(best_column)]
            if self.tree[row][4] == 0:
                if column_value <= self.tree[row][1]:
                    return self._query_point(row + 1, point)
                else:
                    return self._query_point(int(row + self.tree[row][3]), point)
            else:
                if column_value < self.tree[row][1]:
                    return self._query_point(row + 1, point)
                else:
                    return self._query_point(int(row + self.tree[row][3]), point)

    def _build_tree(self, data_x, data_y):
        #clear existing tree
        if data_x.shape[0] <= self.leaf_size:
            if self.verbose:
                print("reached leaf base case 1")
            return np.array([-1, data_y.mean(), -1, -1, -1]).reshape((1, -1))
        if np.all(data_y == data_y[0]):
            if self.verbose:
                print("reached leaf base case 2")
            return np.array([-1, data_y[0], -1, -1, -1]).reshape(1, -1)
        #Determine the best feature
        max_abs_corr = -1
        max_corr_index = -1
        for i in range(data_x.shape[1]):
            corr_coef = abs(np.corrcoef(data_x[:, i], data_y)[0, 1])
            if corr_coef > max_abs_corr:
                max_abs_corr = corr_coef
                max_corr_index = i
        if self.verbose:
            print("The best column is " + str(max_corr_index))
            print(f"The highest correlation is {max_abs_corr}")
        #Determine Split val
        split_val = np.median(data_x[:, max_corr_index])
        if self.verbose:
            print("The splitval is " + str(split_val))
        #split into left and right trees
        config = 0  #0 means <=/>  1 means </>=
        selected_rows_left = data_x[:, max_corr_index] <= split_val
        selected_rows_right = data_x[:, max_corr_index] > split_val
        #edge case handling:
        if np.all(selected_rows_right == False):
            config = 1
            selected_rows_left = data_x[:, max_corr_index] < split_val
            selected_rows_right = data_x[:, max_corr_index] >= split_val
            if np.all(selected_rows_left == False):
                return np.array([-1, data_y.mean(), -1, -1, -1]).reshape((1, -1))
            if self.verbose:
                print("edge case right tree empty detected")
        left_tree = self._build_tree(data_x[selected_rows_left], data_y[selected_rows_left])
        right_tree = self._build_tree(data_x[selected_rows_right], data_y[selected_rows_right])
        if self.verbose:
            print("left tree size is " + str(left_tree.shape[0]))
        root = [max_corr_index, split_val, 1, left_tree.shape[0] + 1, config]
        if self.verbose:
            print("the root added is below:")
            print(root)

        return np.vstack((root, left_tree, right_tree))



