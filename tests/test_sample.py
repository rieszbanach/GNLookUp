def test_classifier():
	
	try:
		import GNLOOKUP.Classifiers.spanish_classifier as classifiers
	except BaseException:
		import sys
		sys.path.append("../")
		sys.path.append("../GNLOOKUP/Classifiers")
		print(sys.path)
	import GNLOOKUP.Classifiers.spanish_classifier as classifiers
	assert classifiers.minimal_performance_metric(classifiers.articles_filenames())[1] >= 0.85



