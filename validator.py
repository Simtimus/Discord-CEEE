import config


def is_valid_group_name(name: str) -> bool:
	split_group_name = name.split('-')
	if len(split_group_name) != 2:
		return False

	if len(split_group_name[0]) != 2:  # Daca nu sunt 2 litere la inceput.
		return False

	if split_group_name[0][0] not in config.uppercase:  # Daca primul simbol nu este litera mare.
		return False

	if split_group_name[0][1] not in config.uppercase and split_group_name[0][1] not in config.lowercase:  # Daca al doilea simbol nu este litara.
		return False

	if len(split_group_name[1]) != 4 and len(split_group_name[1]) != 5:
		return False

	if not str(split_group_name[1][0:3]).isdigit():  # Daca primele 4 numere nu sunt un numar.
		return False

	if len(split_group_name[1]) == 5 and split_group_name[1][-1] not in config.uppercase:  # Dac exista o litera la urma si nu este mica.
		return False

	return True


def is_valid_member_name(name: str) -> bool:
	split_name = name.split(' ')
	if not 1 < len(split_name) < 4:
		return False

	for word in split_name:
		if len(word) < 3:
			return False

		if word[0] not in config.uppercase:
			return False

		i = 1
		while i < len(word):
			if word[i] not in config.lowercase:
				return False
			i += 1

	return True
