import random

f = open("/tests/test-TD-2.tim", "w")

f.write ("#!grid both\n")
f.write ("#!tick 100\n")
f.write ("#!tran 12\n")
#string = "zhfFrRPpDXdx";
string = "DXdxz";
color = 'aAbBcCdgGmkoOpPrtvwyY'
#string = "///zXxdD";
for i in range (100):
	lastWasColor = False
	toss = random.randrange(0, 2)
	if toss > 0:
		if lastWasColor == False:
			s = str(i)+';$' + color[random.randrange(0, len(color))]
			lastWasColor = True
		else:
			s = str(i)+';'
	else:
		s = str(i)+';'

	for j in range (15):
		toss2 = random.randrange(0, 2)
		if toss2 > 0:
			if lastWasColor == False:
				s += '$' + color[random.randrange(0, len(color))]
				lastWasColor = True
		s += str(random.randrange(0, 9))
		s += string[random.randrange(0, len(string))]
		lastWasColor = False
	s += '\n'
	f.write(s)

f.close()
