# PowerLotto Draws Every Saturday at 9:00 p.m.
# 6/55 Grand Lotto draw schedule is held every Mondays, Wednesdays and Saturdays.
# 6/49 SuperLotto Draws Every Tuesday, Thursday and Sunday at 9:00 p.m.
# 6/45 MegaLotto Draws Every Monday, Wednesday and Friday at 9:00 p.m.
# 6/42 Lotto Draws Every Tuesday and Saturday at 9:00 p.m.

import time
import random

# Generate seed
#initial_seed = int(round(time.time() * 1000))
initial_seed = int(time.time() * 1000000)
#offset = 1000 * 11 * 60 * 60
offset = 0
seed = initial_seed + offset

print ('seed: {} ({} + {})'.format(seed, initial_seed, offset))
print ('')

def draw_num(draw_count, lotto_nums):
	max_draw_count = draw_count
	max_length = len(lotto_nums)

	picked = []
	thrown = []

	while draw_count > 0 and len(lotto_nums) > 0:
		length = len(lotto_nums)
		drawn_num = lotto_nums.pop(int(random.random() * length))
		if int(random.random() * 10) > 4:
			# Draw number
			picked.append(drawn_num)
			draw_count -= 1
		else:
			# Throw away number
			thrown.append(drawn_num)

	# Display results
	print ('Lotto {}/{}'.format(max_draw_count, max_length))
	print ('  Picked: {}'.format(picked))
	print ('  Thrown: {}'.format(thrown))
	print ('')

# Lotto configuration
draw_count = 6
lotto_42_max = 42
lotto_45_max = 45
lotto_49_max = 49
lotto_55_max = 55
lotto_65_max = 65

#seed = 1 # Todo: comment on live
random.seed(seed)

# Lotto numbers container
lotto_42_nums = []
lotto_45_nums = []
lotto_49_nums = []
lotto_55_nums = []
lotto_65_nums = []

loop_cnt = 1996
for i in range(1, loop_cnt + 1):
	lotto_42_nums.clear()
	lotto_45_nums.clear()
	lotto_49_nums.clear()
	lotto_55_nums.clear()
	lotto_65_nums.clear()

	max_num = max(lotto_42_max, lotto_45_max, lotto_49_max, lotto_55_max, lotto_65_max)
	for i in range (1, max_num + 1):
		if i <= lotto_42_max:
			lotto_42_nums.append(i)
		if i <= lotto_45_max:
			lotto_45_nums.append(i)
		if i <= lotto_49_max:
			lotto_49_nums.append(i)
		if i <= lotto_55_max:
			lotto_55_nums.append(i)
		if i <= lotto_65_max:
			lotto_65_nums.append(i)

	# Draw numbers
	#draw_num(draw_count, lotto_42_nums)
	#draw_num(draw_count, lotto_45_nums)
	#draw_num(draw_count, lotto_49_nums)
	draw_num(draw_count, lotto_55_nums)
	#draw_num(draw_count, lotto_65_nums)
