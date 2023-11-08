import numpy as np


class RTLearner(object):
    """
    This is a Random Tree Learner

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
            if self.verbose:
                print("AT LEAF")
                print(f"current row: {row}")
                if np.isnan(self.tree[row][1]):
                    print("NAN VALUE FOUND")
            return self.tree[row][1]
        else:
            best_column = self.tree[row][0]
            column_value = point[int(best_column)]
            if self.tree[row][4] == 0:
                if column_value <= self.tree[row][1]:
                    if self.verbose:
                        print(f"current row: {row}")
                    return self._query_point(row + 1, point)
                else:
                    if self.verbose:
                        print(f"current row: {row}")
                    return self._query_point(int(row + self.tree[row][3]), point)
            else:
                if column_value < self.tree[row][1]:
                    if self.verbose:
                        print(f"current row: {row}")
                    return self._query_point(row + 1, point)
                else:
                    if self.verbose:
                        print(f"current row: {row}")
                    return self._query_point(int(row + self.tree[row][3]), point)

    def _build_tree(self, data_x, data_y):
        if self.verbose:
            print(f"size of x data: {data_x.shape}")
            print(f"size of y data:{data_y.shape}")
        if data_y.shape[0] == 0:
            if self.verbose:
                print("data_y is empty")
                print(data_x)
                print(data_y)
        if data_x.shape[0] <= self.leaf_size:
            # if self.verbose:
            #     print("reached leaf base case 1")
            return np.array([-1, data_y.mean(), -1, -1, -1]).reshape((1, -1))
        if np.all(data_y == data_y[0]):
            # if self.verbose:
            #     print("reached leaf base case 2")
            return np.array([-1, data_y[0], -1, -1, -1]).reshape(1, -1)
        #Determine random feature and splitVal
        random_feature = np.random.randint(0, data_x.shape[1] - 1)
        random_row_val1 = np.random.randint(0, data_x.shape[0] - 1)
        random_row_val2 = np.random.randint(0, data_x.shape[0] - 1)
        random_split_val = (data_x[random_row_val1, random_feature] + data_x[random_row_val2, random_feature])/2

        # if self.verbose:
        #     print("The random column is " + str(random_feature))
        #     print("The splitval is " + str(random_split_val))
        #split into left and right trees
        config = 0  #0 means <=/>  1 means </>=
        selected_rows_left = data_x[:, random_feature] <= random_split_val
        selected_rows_right = data_x[:, random_feature] > random_split_val

        #edge case handling:
        if np.all(selected_rows_right == False):
            config = 1
            selected_rows_left = data_x[:, random_feature] < random_split_val
            selected_rows_right = data_x[:, random_feature] >= random_split_val
            if np.all(selected_rows_left == False):
                return np.array([-1, data_y.mean(), -1, -1, -1]).reshape((1, -1))
            # if self.verbose:
            #     print("edge case right tree empty detected")
        if self.verbose:
            if random_split_val == 0:
                print("--------------SPLITVAL EQUALS 0----------------------------------")
                print(f"x data:{data_x}")
                print(f"y data:{data_y}")
                print(f"random feature: {random_feature}")
                print(f"random row val 1: {random_row_val1}")
                print(f"random row val 2: {random_row_val2}")
                print(f"config: {config}")
                print(f"selected rows left: {selected_rows_left}")
                print(f"selected rows right: {selected_rows_right}")
                print(f"left tree data: {data_x[selected_rows_left]}")
                print(f"right tree data: {data_x[selected_rows_right]}")

        left_tree = self._build_tree(data_x[selected_rows_left], data_y[selected_rows_left])
        right_tree = self._build_tree(data_x[selected_rows_right], data_y[selected_rows_right])
        # if self.verbose:
        #     print("left tree size is " + str(left_tree.shape[0]))
        root = [random_feature, random_split_val, 1, left_tree.shape[0] + 1, config]
        # if self.verbose:
        #     print("the root added is below:")
        #     print(root)
        if self.verbose:
            print(f"current length of tree is: {self.tree.shape[0]}")
        return np.vstack((root, left_tree, right_tree))
