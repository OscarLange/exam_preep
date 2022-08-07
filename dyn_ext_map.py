curr_size = 1
combined_size = curr_size
factor = 0.25
iteration = 0
max_size = 1000

#this calculates the extends (iteration) needed to get the wanted max segment (max_size) size (combined_size)
#with given start size (curr_size) and growth factor (factor)

def round_down(x):
    y = round(x, 2)
    if(y > x):
        return round(y - 0.01, 2)
    return y

while(combined_size < max_size):
    iteration += 1
    curr_size += (curr_size * factor)
    curr_size = round_down(curr_size)
    combined_size += curr_size
    print("X: " + str(curr_size) + ", Y: " + str(combined_size) + ",I: " + str(iteration))
