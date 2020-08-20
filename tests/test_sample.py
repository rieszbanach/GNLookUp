# content of test_sample.py

print('ENTRO AQUI DESDE TESTPY')




def inc(x):
    return x + 1


def test_answer():
    assert inc(3) == 4




#print(dir(classifiers))
    
def test_answerTwo():
	
	try:
		import GNLOOKUP.Classifiers.spanish_classifier as classifiers
	except BaseException:  # (ImportError, ModuleNotFoundError):
		import sys
		sys.path.append("../")
		sys.path.append("../GNLOOKUP/Classifiers")
		print(sys.path)
	import GNLOOKUP.Classifiers.spanish_classifier as classifiers
	assert classifiers.minimal_performance_metric(classifiers.articles_filenames())[1] >= 0.85


