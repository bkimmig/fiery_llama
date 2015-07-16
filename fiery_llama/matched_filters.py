import numpy as np
import pandas as pd
import latbin


def lineify(df, n, column):
    return cubeify(df, [n], [column])


def squareify(df, nx, ny, xcol, ycol):
    return cubeify(df, [nx, ny], [xcol, ycol])


def cubeify(df, n, columns, target="weights"):
    cube_df = pd.DataFrame()
    cube_df[target] = df[target]

    for i, col in enumerate(columns):
        cdx = (np.max(df[col]) - np.min(df[col]))/(n[i] - 1)
        cube_df[col] = np.around(df[col]/cdx).astype(int)
        cube_df[col] -= np.min(cube_df[col])
    
    gsum = cube_df.groupby(columns)[target].sum()
    out_cube = np.zeros(n)
    for ind in gsum.index:
        out_cube[ind] = gsum.ix[ind]
    return out_cube


class PointFilter(object):  # like this name???
    def __init__(
            self,
            point_cloud,
            filtered_columns,
            sigma_vec,
    ):
        self.point_cloud = point_cloud
        self.filtered_columns = filtered_columns
        self.sigma_vec = sigma_vec

    def get_weights(self, point_cloud):
        pdata = point_cloud[self.filtered_columns]
        filter_pts = self.point_cloud[self.filtered_columns]
        sim_matrix = latbin.matching.sparse_distance_matrix(
            pdata/self.sigma_vec,
            filter_pts/self.sigma_vec,
        )
        weights = np.asarray(sim_matrix.sum(axis=1)).reshape((-1,))
        normed_weights = weights/len(self.point_cloud)
        return normed_weights
