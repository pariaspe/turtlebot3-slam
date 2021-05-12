import rospy
import numpy as np
import cv2
from nav_msgs.srv import OccupancyGrid

# define grid_resol as 1m so we can match the initial maps


class MyBinaryMap:
    def __init__(self): #service to request binary map creation
        rospy.init_node("binary_service_node")
        rospy.loginfo("service node for binary map creation initialized")
        binary = rospy.Service("/binary_map", OccupancyGrid, self.binaryGrid)


    def binaryGrid(grid):
        grid_resol = 1
        len_x, len_y = np.shape(grid)
        resol_x, resol_y = int(len_x/grid_resol), int(len_y/grid_resol)
        binaryGrid = np.zeros((resol_x,resol_y))
        for i in range(resol_x):
            for j in range(resol_y):
                
                copyMatrix = grid[i*grid_resol:i*grid_resol+grid_resol,j*grid_resol:j*grid_resol+grid_resol].copy()
                np.where(copyMatrix == -1, 100, copyMatrix) # it may be necessary to increase this value in case the laser info goes beyond walls
                # np.where(copyMatrix >= 50, 100, copyMatrix)
                # np.where(copyMatrix < 50, 0, copyMatrix)
                copyMatrix = copyMatrix/100
                binaryGrid[int(i)][int(j)] = int(round(np.mean(copyMatrix, dtype=np.float64),0))

        print(binaryGrid)       
        return(binaryGrid)


def occupancy_to_binary(grid):
    """

    :param grid: occupancy grid with values between 0 and 1, where 0 represent free and 1 obstacle. -1 --> unknown
    :return:
    """
    binary_grid = np.copy(grid)
    binary_grid[binary_grid > 0.5] = 1
    binary_grid[binary_grid < 0.5] = 0
    return binary_grid


def reduce_resolution(grid, new_shape):
    """

    :param grid: occupancy grid
    :param new_shape:
    :return:
    """
    new_grid = np.copy(grid)
    sh = new_shape[0], grid.shape[0]//new_shape[0], new_shape[1], grid.shape[1]//new_shape[1]
    return new_grid.reshape(sh).mean(-1).mean(1)


def grid_to_img(grid):
    """

    :param grid:
    :return:
    """
    img = np.array(grid * 255, dtype=np.uint8)
    return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 0)


# for script testing
if __name__ == "__main__":
    grid = np.random.rand(500, 500)
    print(grid.shape)
    print(grid)

    small = reduce_resolution(grid, (100, 100))
    print(small.shape)
    print(small)

    binarized_grid = occupancy_to_binary(small)
    print(binarized_grid.shape)
    print(binarized_grid)

    cv2.imshow("Map", grid_to_img(grid))
    cv2.imshow("Map Grey", grid_to_img(small))
    cv2.imshow("Map BW", grid_to_img(binarized_grid))
    cv2.waitKey(0)
