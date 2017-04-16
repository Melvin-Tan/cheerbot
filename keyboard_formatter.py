import math

def format(text_list, callback_data_list = [], ncols = 1):
	nrows = math.ceil(len(text_list) / ncols)
	result = []
	for i in range(nrows):
		row_result = []
		for j in range(ncols):
			if i*ncols + j < len(text_list):
				if len(callback_data_list) == 0:
					button = dict(text=text_list[i*ncols + j])
				else:
					button = dict(text=text_list[i*ncols + j], \
						callback_data=callback_data_list[i*ncols + j])
				row_result.append(button)
		result.append(row_result)
	return result
