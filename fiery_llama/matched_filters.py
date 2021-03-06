import numpy as np
import pandas as pd
import re
import latbin


def lineify(df, n, column):
    return cubeify(df, [n], [column])


def squareify(df, nx, ny, xcol, ycol):
    return cubeify(df, [nx, ny], [xcol, ycol])


def cubeify(df, n, columns, target="weights"):
    """bins up a dataframe into a densely sampled cube
    
    n: list 
      the dimensions of the cube
    columns: list
      the column names to bin on
    target: column name
      the column to sum up for each bin
    
    returns
      cube: ndarray
       the "cubeified" data
    """
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


def compress_cloud(df, bin_size=1., npts_out=250):
    """compress a large number of points into a small representative sample
    via multidimensional histogramming and averaging.
    """
    Aparam = latbin.ALattice(len(df.columns), scale=bin_size)
    pts = Aparam.bin(df)
    centers = pts.mean()
    n_in = pts.size()
    cut_idx = min(len(centers), npts_out)
    thresh = np.sort(n_in)[-cut_idx]
    mask = (n_in >= thresh)
    centers['weights'] = n_in/np.sum(n_in[mask])
    centers = centers[mask]
    centers = centers.reset_index()
    colnames = []
    for col in centers.columns:
        if re.match('q_', col) is None:
            colnames.append(col)
    colnames = np.array(colnames)
    centers = centers[colnames].copy()
    return centers


class PointFilter(object):
    """PointFilter handles efficiently calculating distances to 
    a set of points in many dimensions.
    """

    def __init__(
            self,
            point_cloud,
            filtered_columns,
            sigma_vec,
            copy=True,
    ):
        """
        point_cloud: pandas DataFrame
         the points in this filter
        filtered_columns: list
         the column names to filter on
        sigma_vec: ndarray
         the distance scale to use along each dimension
        copy: bool
         if False a copy of the input dataframe will not be made.
        """
        if copy:
            point_cloud = point_cloud.copy()
        self.point_cloud = point_cloud
        if not "weights" in self.point_cloud.columns:
            self.point_cloud["weights"] = np.repeat(
                1.0/len(point_cloud),
                len(point_cloud))
        self.filtered_columns = filtered_columns
        self.sigma_vec = sigma_vec

    def get_weights(self, point_cloud):
        pdata = point_cloud[self.filtered_columns]
        filter_pts = self.point_cloud[self.filtered_columns]
        sim_matrix = latbin.matching.sparse_distance_matrix(
            pdata/self.sigma_vec,
            filter_pts/self.sigma_vec,
        )
        weights = sim_matrix * self.point_cloud["weights"].values
        return weights
