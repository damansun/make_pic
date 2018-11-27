import time
length = 100
total = 3
start_time = time.time()
per_progress = length/total

for i in range(total):
    delta_time = time.time() - start_time + 1
    print(" "*(length - int(per_progress * i)) + "|{}/{} : [{}s, {:.2f} t/s]\r".format(total, i + 1, int(delta_time), i/delta_time), end='', flush=True)
    # [Coulson]: print(" "*200 + "\r", end='')
    print(" {:3d}%|".format(int((i+1)/total * 100)) + "█"*(int(per_progress * (i + 1))), end='')
    time.sleep(1)

print("")
