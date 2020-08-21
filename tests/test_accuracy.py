from .context import *
import GNLOOKUP.Classifiers.spanish_classifier as classifiers


def test_classifiers():

	assert classifiers.accuracy(classifiers.articles_filenames())[1] >= 0.85
