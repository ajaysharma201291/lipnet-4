from __future__ import division
import numpy as np
import contextlib


@contextlib.contextmanager
def printoptions(*args, **kwargs):
    original = np.get_printoptions()
    np.set_printoptions(*args, **kwargs)
    yield
    np.set_printoptions(**original)


class ConfusionTable:
    """
    Confusion table and derived measures
    https://en.wikipedia.org/wiki/Confusion_matrix
    """

    def __init__(self, predictions, labels, class_id, name=""):
        """

        :param predictions: vector with predicted classes
        :param labels: vector with true labels
        :param class_id: integer
        :param name: string
        """
        self.name = name
        mask_predictions = predictions == class_id
        mask_labels = labels == class_id

        self.true_positive = np.count_nonzero(np.logical_and(mask_predictions, mask_labels))

        self.true_negative = np.count_nonzero(np.logical_and(np.logical_not(mask_predictions),
                                                             np.logical_not(mask_labels)))

        self.false_positive = np.count_nonzero(np.logical_and(mask_predictions,
                                                              np.logical_not(mask_labels)))

        self.false_negative = np.count_nonzero(np.logical_and(np.logical_not(mask_predictions),
                                                              mask_labels))

        self.sensitivity = self.true_positive / (self.true_positive + self.false_negative)
        self.specificity = self.true_negative / (self.false_positive + self.true_negative)
        self.precision = self.true_positive / (self.true_positive + self.false_positive)
        self.negative_predictive_value = self.true_negative / (self.true_negative + self.false_negative)
        self.false_positive_rate = 1 - self.specificity
        self.false_discovery_rate = 1 - self.precision
        self.miss_rate = 1 - self.sensitivity


    def __str__(self):
        return '%s tp: %0.4f tn: %0.4f fp: %0.4f fn: %0.4f' % (self.name,
                                                               self.true_positive,
                                                               self.true_negative,
                                                               self.false_positive,
                                                               self.false_negative)


class ConfusionMatrix:
    """
    Confusion matrix class.
    Based on numpy
    """

    def __flatten_one_hot(self, v):
        """

        :param v:
        :return:
        """
        return v.argmax(axis=1)

    def __init__(self, predictions, true_labels, class_names=None):
        """

        :param predictions:
        :param true_labels:
        """
        assert predictions.shape == true_labels.shape, \
            'Shape of predictions and true labels array must be the same'

        # extract number of classes
        self.__num_classes = predictions.shape[1]

        # make class names
        if class_names is None:
            self.__class_names = []
            for i in xrange(self.__num_classes):
                self.__class_names.append('Class_%d' % i)
        else:
            assert len(class_names) == self.__num_classes,\
                'Number of class names must be equal to total number of classes'
            self.__class_names = class_names

        # extract number of examples
        self.__num_examples = predictions.shape[0]

        # flatten one hot encoded predictions and labels
        _predictions = self.__flatten_one_hot(predictions)
        _labels = self.__flatten_one_hot(true_labels)

        # create placeholder for confusion matrix
        self.__confusion_matrix = np.zeros([self.__num_classes, self.__num_classes])

        # fill confusion matrix
        for i in xrange(self.__num_examples):
            r = _labels[i]
            c = _predictions[i]
            self.__confusion_matrix[r, c] += 1

        # normalize confusion matrix
        row_sums = self.__confusion_matrix.sum(axis=1, keepdims=True)
        self.__confusion_matrix_normalized = self.__confusion_matrix / row_sums

        # create confusion tables for each class
        self.confusion_tables = {}
        for i in xrange(self.__num_classes):
            self.confusion_tables[self.__class_names[i]] = \
                ConfusionTable(_predictions, _labels, i, name=self.__class_names[i])
            #print self.confusion_tables[self.__class_names[i]]

    @property
    def matrix_not_normalized(self):
        return self.__confusion_matrix

    @property
    def matrix_normalized(self):
        return self.__confusion_matrix_normalized

    def print_to_console(self):
        """

        :return:
        """
        with printoptions(precision=4):
            print self.__confusion_matrix
            print '\n'
            print 'Normalized:'
            print self.__confusion_matrix_normalized