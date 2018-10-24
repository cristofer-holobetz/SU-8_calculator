import csv

# Reads type of SU-8 user wants to use and selects correct files



su8type = input('Select SU-8 Type:')

def print_values():
    print(sb_time)
    print(exp_energy)
    print(peb_time)
    print(dev_time)

def choose_resist_range(channel_height):
    range_1 = '2000_5-2015'
    range_2 = '2025-2075'
    range_3 = '2100-2150'

    if 2000.5 <= channel_height <= 2015:
        return range_1
    elif 2025 <= channel_height <= 2075:
        return range_2
    elif 2100 <= channel_height <= 2150:
        return range_3
    else:
        print('This photoresist is either unsupported or does not exist')
        return

# Using HOFs to return a suitable linear function for any input range
def calc_linear_func(channel_height, converted_curve):
    sb_times = converted_curve
    row, col = 0, 0
    while sb_times[row][0] < channel_height:
        row += 1

    def linear_func(x1, y1, x2, y2):
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1

        def func(x):
            return m * x + b

        return func

    return linear_func


def calc_sb_time(channel_height):
    curve_range = choose_resist_range(channel_height)

    with open('assets/sb_times/SB_SU-8_' + curve_range + '.csv', mode='r') as  csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        sb_times = [tuple([val for val in row]) for row in reader]






# def calc_exp_energy(channel_height):

# def calc_peb_time(channel_height):

# def calc_dev_time(channel_height):




file = open("SU-8_Data", "w")

file.write("Hello world\n")
file.write("This is our new text file\n")
file.write("and this is another line.\n")
file.write("Why? Because we can.\n")

file.close()
