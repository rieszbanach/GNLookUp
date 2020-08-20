import re
import time
import itertools
from pathlib import Path

script_location = Path(__file__).absolute().parent
print(script_location)
#file_location = script_location / 'file.yaml'
#file = file_location.open()

# PATTERNS

pattern_1 = '''
delimiter_
non_target_left_expr
target_name
non_target_centr_expr
university
'''

pattern_2 = '''
delimiter
non_target_left_expr
university
non_target_centr_expr
right_expr_with_target_name
delimiter
'''


def words_set(words_filename):
	"""Loads the available words for a given p.o.s. tagging"""
	with open(words_filename, 'r', encoding='utf-8') as f:
		words_list = f.readlines()
	
	words_list = [word.strip('\n') for word in words_list]

	words = tuple(set(words_list))
	
	return words

	
def article_content(article_filename):
	
	with open(script_location / article_filename, 'r', encoding='utf-8') as f:
		article = f.read()
	
	return article
	
sustantives = words_set(script_location / 'glosarium/sustantives.txt')

adjectives = words_set(script_location / 'glosarium/adjectives.txt')

verbs = words_set(script_location / 'glosarium/verbs.txt')

prepositions = words_set(script_location / 'glosarium/prepositions.txt')

conjunctions = words_set(script_location / 'glosarium/conjunctions.txt')

adverbs = words_set(script_location / 'glosarium/adverbs.txt')

pronouns = words_set(script_location / 'glosarium/pronouns.txt')

no_attributes = [verbs, prepositions, conjunctions, adverbs, pronouns]

verb_homonyms = [
	'Facultad', 'Programa', 'Programas', 'Curso', 'Diseño', 'Estudio',
	'Centro', 'Libro', 'Doctorado', 'Redes', 'Medico', 'Trabajo', 'Interna',
	'Internas', 'Medicina', 'Medicinas', 'Proyecto', 'Humana', 'Humanas',
	'Filosofa', 'Filosofas'
]

valid_connectors = set([
	'De', 'Del', 'El', 'La', 'Y', 'Las', 'Los', 'En', 'Con', 'E'
])

banned_terms = set([
	'Otro', 'Otra', 'Parte', 'Por', 'Lo', 'Su', 'Suyo', 'Mio', 'Mi',
	'Vuestro', 'Nuestro'
])

for pos in no_attributes:
	
	banned_terms = banned_terms.union(pos)
	
banned_terms = banned_terms.difference(valid_connectors)

banned_terms = banned_terms.difference(verb_homonyms)

common_proper_nouns = words_set(script_location /
	'glosarium/common_proper_nouns.txt'
)

geographic_prefix = (
	'Puerto', 'San', 'Santa', 'Santo', 'El', 'La', 'Las', 'Los', 'Villa',
	'Pueblo', 'Rio', 'Costa', 'Buen', 'Buenos', 'Llano', 'Lago', 'Laguna',
	'Nueva', 'Nuevo', 'Ciudad', 'Paso', 'Bahia', 'Cabo', 'Golfo', 'Playa',
	'Tierra', 'Monte', 'Puente', 'Sierra', 'Avenida', 'Plaza', 'Edificio'
)

geographic_terms = (
	'Alto', 'Alta', 'Medio', 'Media', 'Bajo', 'Baja', 'New', 'Beach',
	'County', 'Country', 'Long', 'Valley', 'City', 'Town', 'East',
	'West', 'North', 'South', 'Northern', 'Southern', 'Eastern', 'Western',
	'River', 'Heights', 'Lake', 'Sea', 'Hill', 'Hills', 'Island', 'Islands',
	'Mount', 'Port', 'Newport', 'Park', 'Gulf', 'Rock', 'Harbor', 'Harbour',
	'Garden', 'Grand', 'Gran', 'Great', 'Saint', 'St', 'Sainte', 'Falls',
	'Grove', 'Little', 'Village', 'Ville', 'Plaine', 'Plaines', 'Mountain',
	'Point', 'Bay', 'Creek', 'Rapids', 'Springs', 'Fort', 'Cape',
	'Ridge', 'Highland', 'Nova', 'Avenue', 'Square', 'Building', 'Street',
	'Square'
)

publications_nouns = (
	'Review', 'Journal', 'Magazine', 'Post', 'The', 'Annual', 'Quarterly',
	'Monthly', 'Weekly', 'Daily', 'Nightly', 'Proceedings', 'Annals',
	'Advances', 'Applications', 'Applied', 'Research', 'Letters', 'Notes',
	'Theory', 'Acta', 'Studies', 'Transactions', 'News', 'Notices',
	'Society', 'Bulletin', 'Communications', 'Association', 'International',
	'Science', 'Engineering', 'Economics'
)


def articles_classifier(
		article_filename,
		univ='Universidad de Antioquia',
		prof='Ignacio Ramon Ferrin Vasquez',
		surname='Ferrin'):
			
	"""
	Approves or not the likelihood of a relationship between the target name
	and the university appearing simultaneously in a spanish-written
	news article
	"""
	
	time_0 = time.time()
	
	rejected = []

	article = diacritics_filter(article_content(article_filename))
	
	pattern_matches_list = patterns_finder(
		article,
		univ,
		prof,
		surname
	)
	
	pattern_separators = [pattern_1_separator, pattern_2_separator]
	
	for idx, pattern_matches in enumerate(pattern_matches_list):
		
		for pattern_match in pattern_matches:
			
			approval = pattern_separators[idx](pattern_match)
			
			if approval[0]:
				
				print(time.time() - time_0, 'exec_time')
				
				return approval
				
			else:
				
				rejected.append((approval[1], approval[2]))
				
	return [False, rejected]

	
def pattern_1_separator(pattern_1_match):
		"""
		Approves or not the likelihood of a relationship between the target name
		and the university appearing simultaneously in a pattern_1 text
		"""
		
		match = pattern_1_match

		(
			left_expr,
			_,
			centr_expr,
			_
		) = match.groups()
		
		relevant_left_expr = relevant_expr(
			left_expr,
			direction='BACKWARD'
		)
		
		left_expr_prof_attributes = professor_attributes(
			relevant_left_expr,
			direction='BACKWARD',
			zone='LEFT_EXPR'
		)
													
# LEFT_CENTR_EXPR
		
		relevant_left_centr_expr = relevant_expr(
			centr_expr,
			direction='FORWARD'
		)
		
		left_centr_expr_prof_attributes = professor_attributes(
			relevant_left_centr_expr,
			direction='FORWARD',
			zone='LEFT_CENTR_EXPR'
		)

# RIGHT_CENTR_EXPR
		
		relevant_right_centr_expr = relevant_expr(
			centr_expr,
			direction='BACKWARD'
		)
		
		right_centr_expr_prof_attributes = professor_attributes(
			relevant_right_centr_expr,
			direction='BACKWARD',
			zone='RIGHT_CENTR_EXPR'
		)
		
		pattern_1_prof_attributes = (
			left_expr_prof_attributes
			+ left_centr_expr_prof_attributes
			+ right_centr_expr_prof_attributes
		)
			
		print(pattern_1_prof_attributes, 'pattern_1_prof_attributes')
			
		print('\n')
		
		no_coworker = at_least_one_person(centr_expr)
		
		if not no_coworker:
			
			return [True, match.group(0)]
			
		return [False, match.group(0), no_coworker]


def pattern_2_separator(pattern_2_match):
		"""
		Approves or not the likelihood of a relationship between the target name
		and the university appearing simultaneously in a pattern_2 text
		"""
		
		print('pattern_2_separator\n')

		match = pattern_2_match
		
		(
			non_target_left_expr,
			_,
			non_target_centr_expr,
			right_expr,
			expr_after_target
		) = match.groups()
		
		print(non_target_centr_expr, 'non_target_centr_expr')
		print(right_expr,'right_expr')
		print(expr_after_target, 'expr_after_target')
		
		pattern_2_relevant_left_expr = relevant_expr(
			non_target_left_expr,
			direction='BACKWARD')
		
		pattern_2_left_expr_prof_attributes = professor_attributes(
			pattern_2_relevant_left_expr,
			direction='BACKWARD',
			zone='PATTERN_2_LEFT_EXPR')
				
# PATTERN_2_LEFT_CENTR_EXPR
		
		pattern_2_relevant_left_centr_expr = relevant_expr(
			non_target_centr_expr,
			direction='FORWARD'
		)
		
		pattern_2_left_centr_expr_prof_attributes = professor_attributes(
			pattern_2_relevant_left_centr_expr,
			direction='FORWARD',
			zone='PATTERN_2_LEFT_CENTR_EXPR'
		)
						
# PATTERN_2_RIGHT_CENTR_EXPR
		
		pattern_2_relevant_right_centr_expr = relevant_expr(
			non_target_centr_expr,
			direction='BACKWARD'
		)
		
		pattern_2_right_centr_expr_prof_attributes = professor_attributes(
			pattern_2_relevant_right_centr_expr,
			direction='BACKWARD',
			zone='PATTERN_2_RIGHT_CENTR_EXPR'
		)
		
# PATTERN_2_RIGHT_EXPR
		
		pattern_2_relevant_right_expr = relevant_expr(
			expr_after_target,
			direction='FORWARD'
		)
		
		pattern_2_right_expr_prof_attributes = professor_attributes(
			pattern_2_relevant_right_expr,
			direction='FORWARD',
			zone='PATTERN_2_RIGHT_EXPR'
		)
		
		print('\n')
		
		pattern_2_prof_attributes = (
			pattern_2_left_expr_prof_attributes
			+ pattern_2_left_centr_expr_prof_attributes
			+ pattern_2_right_centr_expr_prof_attributes
			+ pattern_2_right_expr_prof_attributes
		)
			
		print(pattern_2_prof_attributes, 'pattern_2_prof_attributes')
			
		print('\n')
		
		no_coworker = at_least_one_person(
			non_target_centr_expr
		)
		
		slide_pattern = re.compile('(?:^\\s*\.$)|(?:^\\s*\\n$)')
		
		is_slide = (
			True if (
				slide_pattern.findall(expr_after_target)
				and non_target_centr_expr[-1] == '\n'
			)
			else
			False
		)
		if not no_coworker and not is_slide:
			
			return [True, match.group(0)]
			
		return [False, match.group(0), no_coworker]


def is_member_of(word, pos):
	
	return word.strip('s') in pos or word.strip('es') in pos
		

def is_plural(
	word,
	sustantives=sustantives,
	adjectives=adjectives):
	
	return (
		(
			is_member_of(word, sustantives) or is_member_of(word, adjectives)
		)
		and (
			word[-1] == 's' or word[-2:] == 'es'
		)
		and len(word) > 4
	)


def coditions(capitalized_word, word):
	
	yield word[0].isupper()
	
	yield capitalized_word in banned_terms
	
	yield capitalized_word in valid_connectors

	
def probable_person_names(possible_person_match):
	
	possible_person = possible_person_match.groups()[0]
	
	possible_person = possible_person[:-1]
	
	print(possible_person, 'possible_person_before')
	
	(possible_person.strip('\s')).strip(' ')
	
	print(possible_person, 'possible_person')

	possible_person = (
		possible_person.strip(',')
		.strip('.')
		.strip('\n')
	)
	
	possible_person_names = possible_person.split(' ')
	
	print(possible_person_names, 'possible_person_names')
	
	return possible_person, possible_person_names
	

def at_least_one_person(
		centr_expr,
		sustantives=sustantives,
		adjectives=adjectives):
	
	possible_person_pattern = re.compile(
		"("
		"(\\b[A-Z][a-záéíóúüñ]{3,}\\b )"
		"(\\b[A-Z][a-záéíóúüñ]{3,}\\b( |,|.|$)){1,3}"
		")"
	)
	
	possible_person_matches = possible_person_pattern.finditer(centr_expr)
	
	people = []
	
	for match in possible_person_matches:
		
		possible_person, possible_person_names = probable_person_names(match)
		
		possible_person, possible_person_names = connectors_filter(
			possible_person, possible_person_names)
		
		if len(possible_person_names) < 2:
			
			continue
		
		if is_non_person(possible_person_names):
			
			continue
		
		if len(possible_person_names) >= 4:
			
			if not is_coworker(possible_person_names):
				people.append(possible_person)
			
			continue
			
		elif len(possible_person_names) == 3:
			
			if not is_coworker(possible_person_names):
				people.append(possible_person)
			
			continue

		if (
			possible_person_names[1].strip('s') not in adjectives
			and possible_person_names[1].strip('es') not in adjectives
		):
			
			if (
				not is_coworker(possible_person_names)
				and not is_a_company(possible_person_names)
			):
				people.append(possible_person)
			
			continue
						
		if (
			possible_person_names[0].strip('s') not in sustantives
			and possible_person_names[0].strip('es') not in sustantives
		):
			
			if not is_coworker(possible_person_names):
				people.append(possible_person)
			
			continue
			
		if (possible_person_names[0] in common_proper_nouns):
			
			if not is_coworker(possible_person_names):
				people.append(possible_person)
			
			continue
			
	return people


def patterns_finder(
		article,
		univ='Universidad de Antioquia',
		prof='Ignacio Ramon Ferrin Vasquez',
		surname='Ferrin'):
	
	all_professor_names = prof.replace(surname, 'SURNAME', 1)
	# Nobody is supposed to have any surname equal to any given name
	
	print(all_professor_names, 'all_professor_names')
	
	all_professor_names = all_professor_names.split(' ')
	
	first_surname_idx = all_professor_names.index('SURNAME')
	
	professor_given_names = all_professor_names[:first_surname_idx]
	
	print(professor_given_names, 'professor_given_names')
	
	second_surname = ''
	
	for word in all_professor_names[first_surname_idx+1:]:
		
		second_surname += word
	
# Everyone's supposed to have two surnames, no matter whether they are composed

	combinations = []

	for p in range(1, len(professor_given_names) + 1):
		combinations += list(itertools.combinations(professor_given_names, p))
		
	composed_forenames_groups = []
		
	for combi in combinations:
		
		composed_forename = combi[0]
		
		for forename in combi[1:]:
			
			composed_forename += '\\s' + forename
		
		composed_forename_group = '(?:' + composed_forename + ')'
		
		composed_forenames_groups.append(composed_forename_group)
		
	composed_forename_regex = composed_forenames_groups[0]
	
	for composed_forename_group in composed_forenames_groups[1:]:
		
		composed_forename_regex += '|' + composed_forename_group
		
	composed_forename_regex = '(?:' + composed_forename_regex + ')'
	
	any_valid_professor_name_regex = (
		composed_forename_regex
		+ '(?:\\s{})(?:\\s{})*'.format(surname, second_surname)
	)
	
	print(article)
	
	any_valid_professor_name_pattern = re.compile(any_valid_professor_name_regex)
	
	professor_mentions = any_valid_professor_name_pattern.finditer(article)
	
	for match in professor_mentions:
		
		print(match.group(0), 'professor_mention')
	
	pattern_1 = re.compile(
		"((?:^|\.|\\n)(?:(?!\.)(?!{Apellido}).|\\n)*)"
		"({Nombre})"
		"((?:(?!{Apellido}).|\\n)*?)"
		"({Universidad})+".format(
			Apellido=any_valid_professor_name_regex,
			Nombre=any_valid_professor_name_regex,
			Universidad=univ
		)
	)
	
	pattern_1_matches = pattern_1.finditer(article)

	pattern_2 = re.compile(
		"((?:(?!\.)(?!{Apellido})(?!{Universidad}).|\\n)*)"
		"((?:de|en) la {Universidad})"
		"((?:(?!{Apellido})(?!{Universidad}).|\\n)*)"
		"({Nombre}(.*?(?:\.|\\n)))".format(
			Apellido=any_valid_professor_name_regex,
			Nombre=any_valid_professor_name_regex,
			Universidad=univ
		)
	)
	
	pattern_2_matches = pattern_2.finditer(article)
	
	return [pattern_1_matches, pattern_2_matches]

diacritized_pattern = re.compile('([áéíóúÁÉÍÓÚ])')


def no_diacritized(diacritized_vowel):
	if diacritized_vowel == 'á':
		return 'a'
	if diacritized_vowel == 'é':
		return 'e'
	if diacritized_vowel == 'í':
		return 'i'
	if diacritized_vowel == 'ó':
		return 'o'
	if diacritized_vowel == 'ú':
		return 'u'
	if diacritized_vowel == 'Á':
		return 'A'
	if diacritized_vowel == 'É':
		return 'E'
	if diacritized_vowel == 'Í':
		return 'I'
	if diacritized_vowel == 'Ó':
		return 'O'
	if diacritized_vowel == 'Ú':
		return 'U'
	return diacritized_vowel
		
	
def diacritics_filter(text, diacritized_pattern=diacritized_pattern):
	
	return diacritized_pattern.sub(
		lambda x: no_diacritized(x.groups()[0]),
		text
	)


def article_classifier_helper(article_filename):

	with open(script_location / 'samples/articles_metadata.txt', 'r', encoding='utf-8') as f:
		articles_min_metadata = f.read()
	
	metadata_pattern = re.compile('{},(.+?),(.+?),'.format(article_filename))
	
	minimal_metadata = metadata_pattern.finditer(articles_min_metadata)
	
	for match in minimal_metadata:
		
		researcher, last_name = match.groups()
		
	return articles_classifier(
		'samples/{}'.format(article_filename),
		univ='Universidad de Antioquia',
		prof=researcher,
		surname=last_name
	)

	
def all_persons_finder(
		centr_expr,
		sustantives=sustantives,
		adjectives=adjectives):
	
	possible_person_pattern = re.compile(
		"("
		"(\\b[A-Z][a-záéíóúüñ]+\\b )"
		"(\\b[A-Z][a-záéíóúüñ]+\\b( |,|.|$)){1,3}"
		")"
	)
	
	possible_person_matches = possible_person_pattern.finditer(centr_expr)
	
	people = []
	
	for match in possible_person_matches:
		
		possible_person, possible_person_names = probable_person_names(match)
		
		if len(possible_person_names) >= 4:
			
			people.append(possible_person)
			
			continue
			
		if len(possible_person_names) == 3:
			
			people.append(possible_person)
			
			continue
		
		if (
			not is_member_of(possible_person_names[1], adjectives)
			and not is_member_of(possible_person_names[1], verbs)
		):
			
			people.append(possible_person)
			
			continue
			
		if not is_member_of(possible_person_names[0], sustantives):
			
			people.append(possible_person)
					
	return people

	
def relevant_expr(full_expr, direction='BACKWARD'):
	
	if direction == 'BACKWARD':
		
		relevant_sub_expr = full_expr.split('\n')[-1]
		
		relevant_sub_expr = full_expr.split('.')[-1]
		
		relevant_sub_expr = relevant_sub_expr.split(';')[-1]
		
	if direction == 'FORWARD':
		
		relevant_sub_expr = full_expr.split('\n')[0]
		
		relevant_sub_expr = relevant_sub_expr.split('.')[0]
		
		relevant_sub_expr = relevant_sub_expr.split(';')[0]
	
	return relevant_sub_expr

	
def relevant_terms(relevant_expr, direction):
	
	number_pattern = re.compile('\\d+')
	
	found_numbers = number_pattern.findall(relevant_expr)
	
	if found_numbers:
		
		relevant_expr = relevant_expr.split(found_numbers[-1])[-1] if (
			direction == 'BACKWARD'
		) else (
				relevant_expr.split(found_numbers[0])[0]
		)
		
	word_pattern = re.compile('\\b[\\w]+\\b')
	
	rlvnt_words = word_pattern.findall(relevant_expr)
	
	if direction == 'BACKWARD':
	
		rlvnt_words.reverse()
	
	return rlvnt_words

	
def professor_attributes(
		relevant_expr,
		direction='BACKWARD',
		zone='LEFT_EXPR'):
	
	relevant_expr = relevant_expr
	
	expr_people = all_persons_finder(
		relevant_expr,
		sustantives=sustantives,
		adjectives=adjectives
	)
	
	relevant_words = relevant_terms(relevant_expr, direction)
	
	return (
		with_people(relevant_words, direction) if expr_people
		else (
			without_people(relevant_words, direction)
		)
	)
	
	
def with_people(relevant_words, direction):
	
	attributes = []
	
	if (
		direction == 'BACKWARD'
		and len(relevant_words) > 3
		and people_at_right(relevant_words)
	):
				
		for word in relevant_words:
	
			capitalized_word = word[0].upper() + word[1:]
			
			if (
				not any(coditions(capitalized_word, word))
				and is_plural(capitalized_word)
			):
				
				attributes.append(word)
				
				break
		
		if attributes:
			attributes.reverse()
	
	return attributes
	

def without_people(relevant_words, direction):
	
	attributes = []
	
	for word in relevant_words:
		
		capitalized_word = word[0].upper()+word[1:]
		
		if capitalized_word in banned_terms:
			
			break
		
		if word[0].isupper():
			
			attributes.append(word)
			
			continue
			
		if capitalized_word in valid_connectors:
			
			continue
						
		if (
			is_member_of(capitalized_word, adjectives)
			or is_member_of(capitalized_word, sustantives)
		):
			
			attributes.append(word)
			
			continue
			
		elif True:
			
			break
	
	if attributes and direction == 'BACKWARD':
		attributes.reverse()

	return attributes

	
def people_at_right(relevant_words):
	
	return (
		(
			relevant_words[0][0].isupper()
			and relevant_words[1][0].isupper()
		)
		or (
			relevant_words[0][0] in ['y', 'e']
			and relevant_words[1][0].isupper()
			and relevant_words[2][0].isupper()
		)
	)


def full_name_pattern(partial_person_name):
	
	complete_name_pattern = '(\\b[A-Z][a-záéíóúüñ]+\\b )*'
	
	for name in partial_person_name[:-1]:
		
		complete_name_pattern += (
			name
			+ ' '
			+ '(\\b[A-Z][a-záéíóúüñ]+\\b )*?'
		)
		
	complete_name_pattern += (
		partial_person_name[-1]
		+ '( \\b[A-Z][a-záéíóúüñ]+\\b(\\s|,|.|$))*'
	)
		
	return complete_name_pattern
	

def is_coworker(partial_person_name):
	
	coworker_pattern = full_name_pattern(partial_person_name)
	
	coworker = re.compile(coworker_pattern)
		
	with open(script_location / 'samples/researchers.txt', 'r', encoding='utf-8') as f:
		researchers = f.read()
	
	coworker_matches = coworker.finditer(researchers)
	
	try:
		
		coworker_matches.__next__()
		
		print('{} is a coworker'.format(partial_person_name))
		
		return True
		
	except StopIteration:
		
		print('{} is NOT a coworker'.format(partial_person_name))
		
		return False


def is_non_person(possible_person_names):
	
	return (
		is_a_place(possible_person_names)
		or is_a_publication(possible_person_names)
		or is_a_university(possible_person_names)
	)

	
def is_a_place(possible_person_names):
	
	return (
		(possible_person_names[0] in geographic_prefix)
		or any(name in geographic_terms for name in possible_person_names)
	)

	
def is_a_publication(possible_person_names):
	
	return any(name in publications_nouns for name in possible_person_names)


def is_a_university(possible_person_names):
	
	university_pattern = re.compile(
		"(?:Univer(?:s|z)i)"
		"|(?:Institu)"
		"|(?:Skol(?:a|e))"
		"|(?:School)"
		"|(?:Escuela)"
		"|(?:Scuola)"
		"|(?:Ecole)"
		"|(?:Mater)"
	)
	
	return (
		any(university_pattern.findall(name) for name in possible_person_names)
	)
	
	
def is_a_company(possible_person_names):
	
	return (
		possible_person_names[0].strip('s') in sustantives
		and possible_person_names[0].strip('s') not in common_proper_nouns
	)
	
	
def connectors_filter(possible_person, possible_person_names):
	
	connectors = []
	
	for pos in [prepositions, conjunctions, pronouns, adverbs]:
		
		connectors += list(pos)
	
	if possible_person_names[0] not in connectors:
		
		return [possible_person, possible_person_names]
		
	possible_person = possible_person[len(possible_person_names[0]) + 1:]
		
	return [possible_person, possible_person_names[1:]]
	

def article_label(article_filename):

	with open(script_location / 'samples/articles_metadata.txt', 'r', encoding='utf-8') as f:
		articles_min_metadata = f.read()
	
	article_line_pattern = re.compile('{},(.+\\n?)'.format(article_filename))
	
	article_line_matches = article_line_pattern.finditer(articles_min_metadata)
	
	for match in article_line_matches:
		
		line = match.groups()[0]
		
		label = line.split(',')[-1].strip('\n')
		
	return label
	
	
def minimal_performance_metric(articles_filenames):
	
	start = time.time()
	
	hits = 0
	
	errors = []
	
	for article_filename in articles_filenames:
		
		classification = article_classifier_helper(article_filename)[0]
		
		if (str(classification) == article_label(article_filename)):
			
			hits += 1
			
		else:
			
			errors.append(article_filename)
		
#		hits += 1 if (str(classification) == article_label(article_filename)) else 0
		
	accuracy = hits/len(articles_filenames)
	
	return (hits, accuracy, errors, time.time()-start)


def articles_filenames():

	with open(script_location / 'samples/articles_metadata.txt', 'r', encoding='utf-8') as f:
		articles_min_metadata = f.readlines()
	
	articles_filena = [line.split(',')[0] for line in articles_min_metadata]
		
	return articles_filena
	

def confusion_matrix(articles_filenames):
	
	positives = 0
	
	negatives = 0
	
	true_positives = 0
	
	false_positives = 0
		
	for article_filename in articles_filenames:
		
		label = article_label(article_filename)
		
		classification = str(article_classifier_helper(article_filename)[0])
		
		if label == 'True':
			
			positives += 1
			
			if classification == 'True':
				
				true_positives += 1
				
		else:
			
			if classification == 'True':
				
				false_positives += 1
			
	tpr = true_positives/positives
	
	negatives = len(articles_filenames) - positives
	
	fpr = false_positives/negatives
	
	return [tpr, fpr, positives, negatives]
