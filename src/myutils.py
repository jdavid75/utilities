

def is_power2(num):
	return ((num & (num - 1)) == 0) and num != 0
