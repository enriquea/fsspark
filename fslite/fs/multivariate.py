import logging
from typing import List

import numpy as np
from scipy.stats import spearmanr

from fslite.fs.constants import (
    get_fs_multivariate_methods,
    is_valid_multivariate_method,
)
from fslite.fs.fdataframe import FSDataFrame
from fslite.fs.methods import FSMethod, InvalidMethodError
from fslite.fs.utils import find_maximal_independent_set, percentile_rank

logging.basicConfig(format="%(levelname)s (%(name)s %(lineno)s): %(message)s")
logger = logging.getLogger("FS:MULTIVARIATE")
logger.setLevel(logging.INFO)


class FSMultivariate(FSMethod):
    """
    The FSMultivariate class is a subclass of the FSMethod class and is used for multivariate
    feature selection methods. It provides a way to select features using different multivariate methods such as
    multivariate correlation and variance.

    Example Usage
    -------------
    # Create an instance of FSMultivariate with multivariate_method='m_corr'
    fs_multivariate = FSMultivariate(multivariate_method='m_corr')

    # Select features using the multivariate method
    selected_features = fs_multivariate.select_features(fsdf)
    """

    valid_methods = get_fs_multivariate_methods()

    def __init__(self, fs_method: str, **kwargs):
        """
        Initialize the multivariate feature selection method with the specified parameters.

        Parameters:
            fsdf: The data frame on which feature selection is to be performed.
            fs_method: The multivariate method to be used for feature selection.
            kwargs: Additional keyword arguments for the feature selection method.
        """

        super().__init__(fs_method, **kwargs)
        self.validate_method(fs_method)

    def validate_method(self, multivariate_method: str):
        """
        Validate the multivariate method.

        Parameters:
            multivariate_method: The multivariate method to be validated.
        """

        if not is_valid_multivariate_method(multivariate_method):
            raise InvalidMethodError(
                f"Invalid multivariate method: "
                f"{multivariate_method}. Accepted methods are {', '.join(self.valid_methods)}"
            )

    def select_features(self, fsdf: FSDataFrame):
        """
        Select features using the specified multivariate method.
        """

        return self.multivariate_filter(
            fsdf, multivariate_method=self.fs_method, **self.kwargs
        )

    def multivariate_filter(self,
                            fsdf: FSDataFrame,
                            multivariate_method: str = "m_corr",
                            **kwargs
                            ) -> FSDataFrame:
        """
         Filter features after applying a multivariate feature selector method.

        :param fsdf: Input FSDataFrame
        :param multivariate_method: Multivariate selector method.
                                    Possible values are 'm_corr' or 'variance'.

        :return: Filtered FSDataFrame
        """
        if multivariate_method == "m_corr":
            selected_features = multivariate_correlation_selector(fsdf, **kwargs)
        elif multivariate_method == "variance":
            selected_features = multivariate_variance_selector(fsdf, **kwargs)
            logging.info("Variance method not implemented yet.")
        else:
            raise ValueError(
                f"Invalid multivariate method: {multivariate_method}. "
                f"Choose one of {get_fs_multivariate_methods()}."
            )

        logger.info(f"Applying multivariate filter {multivariate_method}.")

        return fsdf.select_features_by_index(selected_features)

    def __str__(self):
        return f"FSMultivariate(multivariate_method={self.fs_method}, kwargs={self.kwargs})"

    def __repr__(self):
        return self.__str__()


def multivariate_correlation_selector(
        fsdf: FSDataFrame,
        selection_mode: str = 'strict',
        selection_threshold: float = 0.75,
        corr_method: str = "pearson",
) -> List[int]:
    """
    Compute the correlation matrix among input features and select those below a specified threshold.

    :param fsdf: Input FSDataFrame object.
    :param selection_mode: If 'strict' (default), apply hard filtering to remove highly correlated features.
                   Otherwise, 'approximate' find the maximal independent set of highly correlated
                   features (experimental).
    :param selection_threshold: Minimal correlation threshold to consider two features correlated.
    :param corr_method: Correlation method - 'pearson' (default) or 'spearman'.

    :return: List of selected feature indices
    """
    # Retrieve the feature matrix
    f_matrix = fsdf.get_feature_matrix()

    # Get features indexes from matrix
    features_indexes = list(range(f_matrix.shape[1]))

    # Compute correlation matrix
    if corr_method == "pearson":
        corr_matrix = np.corrcoef(f_matrix, rowvar=False)
    elif corr_method == "spearman":
        corr_matrix, _ = spearmanr(f_matrix)
    else:
        raise ValueError(
            f"Unsupported correlation method '{corr_method}'. Use 'pearson' or 'spearman'."
        )

    # Get absolute values of correlations to check magnitude
    corr_matrix = np.abs(corr_matrix)

    # Find pairs of features with correlation above the threshold
    combs_above_cutoff = np.triu(corr_matrix, k=1) > selection_threshold
    correlated_pairs = np.column_stack(np.where(combs_above_cutoff))

    # Set of indices to remove
    index_to_remove = set()
    if selection_mode == "strict":
        # Strict filtering: remove features with higher mean correlations
        col_means = np.mean(corr_matrix, axis=1)
        for i, j in correlated_pairs:
            if col_means[i] > col_means[j]:
                index_to_remove.add(i)
            else:
                index_to_remove.add(j)
    elif selection_mode == "approximate":
        # Experimental approximate method
        index_to_remove = find_maximal_independent_set(correlated_pairs, keep=False)
    else:
        raise ValueError(
            f"Unsupported selection mode '{selection_mode}'. Use 'strict' or 'approximate'."
        )

    # Select feature index to keep
    selected_features = [i for i in features_indexes if i not in index_to_remove]

    return selected_features


def multivariate_variance_selector(fsdf: FSDataFrame,
                                   selection_mode: str = "k_best",
                                   selection_threshold: float = 0.0) -> List[int]:
    """
    Filter features based on variance threshold.

    :param selection_mode: "percentile" or "k_best" (default). If "percentile", the threshold is a percentile of the
                            variance distribution. If "k_best", the threshold is the k highest variances.
                            Default is "k_best" with selection_threshold=0.0 (i.e. remove features with same values
                            in all samples).
    :param fsdf: Input FSDataFrame object.
    :param selection_threshold: Minimal variance threshold to keep a feature.
                               Default is 0.0 (i.e. remove features with same values in all samples).

    :return: List of selected feature indices
    """
    
    # Retrieve the feature matrix
    f_matrix = fsdf.get_feature_matrix()

    # Compute variances (across samples) for each feature
    features_variances = np.var(f_matrix, axis=0)

    # print to log variance mean across features
    logger.info(f"Mean variance across features: {np.mean(features_variances)}")
    print(f"Mean variance across features: {np.mean(features_variances)}")

    if selection_mode == "k_best":
        # keep indices of features with variance above the threshold
        selected_features = np.where(features_variances > selection_threshold)[0]
    elif selection_mode == "percentile":
        # compute the percentile rank of variances
        variances_pct_rank = percentile_rank(features_variances)
        # keep indices of features with variance above the threshold
        selected_features = np.where(variances_pct_rank > selection_threshold)[0]
    else:
        raise ValueError(
            f"Unsupported selection mode '{selection_mode}'. Use 'percentile' or 'k_best'."
        )
    
    logger.info(f"Feature selection mode: {selection_mode}. \n"
                f"Number of features selected: {len(selected_features)}")

    return list(selected_features)
