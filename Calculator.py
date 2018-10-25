import csv

# Reads type of SU-8 user wants to use and selects correct files


su8type = input('Select SU-8 Type:')
channel_height = input('Select desired channel height in µm:')


def print_values():
    spin_speed = calc_spin_speeds(channel_height)
    sb_times = calc_sb_times(channel_height)
    exp_energy = calc_exp_energy(channel_height)
    peb_time = calc_peb_time(channel_height)
    dev_time = calc_dev_time(channel_height)
    print('Spin coat at v1 = 300 rpm, a1 = 100 rpm/s and v2 = ' + spin_speed + ', a2 = 300 rpm/s')
    if len(sb_times) == 2:
        print('Perform Soft Bake for ' + sb_times[0] + ' minutes at 65C and ' + sb_times[1] + ' minutes at 95C.')
    else:
        print('Perform Soft Bake for ' + sb_times + ' minutes.')
    print('Expose surface to ' + exp_energy + ' mJ/cm^2')
    print()
    print(calc_dev_time(channel_height))


def choose_resist_range(height):
    range_1 = '2000_5-2015'
    range_2 = '2025-2075'
    range_3 = '2100-2150'

    if 2000.5 <= height <= 2015:
        return range_1
    elif 2025 <= height <= 2075:
        return range_2
    elif 2100 <= height <= 2150:
        return range_3
    else:
        print('This photoresist is either unsupported or does not exist')
        return

# Using HOFs to return a suitable linear function for any input range


def make_linear_func(height, converted_curve):
    row, col = 0, 0
    while converted_curve[row][0] < height:
        row += 1
    x1 = converted_curve[row][0]
    y1 = converted_curve[row][1]
    x2 = converted_curve[row + 1][0]
    y2 = converted_curve[row + 1][1]

    return linear_func(x1, y1, x2, y2)


def linear_func(x1, y1, x2, y2):
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1

    def func(x):
        return m * x + b

    return func


def calc_spin_speeds(height):
    curve_range = choose_resist_range(height)

    with open('assets/spin_curves/PEB_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        spin_speeds = [tuple([val for val in row]) for row in reader]

        spin_func = make_linear_func(height, spin_speeds)
        return spin_func(height)


def calc_sb_times(height):
    curve_range = choose_resist_range(height)

    with open('assets/sb_times/SB_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        sb_65_times = [(row[0], row[1]) for row in reader]
        sb_65_func = make_linear_func(height, sb_65_times)

        if len(reader[0]) == 3:
            sb_95_times = [(row[0], row[2]) for row in reader]
            sb_95_func = make_linear_func(height, sb_95_times)
            return sb_65_func(height), sb_95_func(height)

        return sb_65_func(height)


def calc_exp_energy(height):
    curve_range = choose_resist_range(height)

    with open('assets/exposure_energies/EE_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        exp_energies = [tuple([val for val in row]) for row in reader]

        ee_func = make_linear_func(height, exp_energies)
        return ee_func(height)


def calc_peb_time(height):
    curve_range = choose_resist_range(height)

    with open('assets/peb_times/PEB_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        peb_times = [tuple([val for val in row]) for row in reader]

        peb_func = make_linear_func(height, [peb_times])
        return peb_func(height)


def calc_dev_time(height):
    curve_range = choose_resist_range(height)

    with open('assets/development_times/PEB_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        develop_times = [tuple([val for val in row]) for row in reader]

        develop_func = make_linear_func(height, [develop_times])
        return develop_func(height)

