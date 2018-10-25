import csv


def print_values(channel_height, resist_type):
    spin_speed = calc_spin_speeds(channel_height, resist_type)
    sb_times = calc_sb_times(channel_height, resist_type)
    exp_energy = calc_exp_energy(channel_height, resist_type)
    peb_time = calc_peb_time(channel_height, resist_type)
    dev_time = calc_dev_time(channel_height, resist_type)
    print('Spin coat at v1 = 300 rpm, a1 = 100 rpm/s and v2 = ' + spin_speed + ', a2 = 300 rpm/s')
    if len(sb_times) == 2:
        print('Perform Soft Bake for ' + sb_times[0] + ' minutes at 65C and ' + sb_times[1] + ' minutes at 95C.')
    else:
        print('Perform Soft Bake for ' + sb_times + ' minutes.')
    print('Expose surface to ' + exp_energy + ' mJ/cm^2')
    print('Perform Post Exposure Bake for ' + peb_time + ' minutes')
    print('Develop wafer for ' + dev_time + ' minutes')


def choose_resist_range(su8_type):
    range_1 = '2000_5-2015'
    range_2 = '2025-2075'
    range_3 = '2100-2150'

    if 2000.5 <= su8_type <= 2015:
        return range_1
    elif 2025 <= su8_type <= 2075:
        return range_2
    elif 2100 <= su8_type <= 2150:
        return range_3
    else:
        print('This photoresist is either unsupported or does not exist')
        return

# Using HOFs to return a suitable linear function for any input range


def make_linear_func(height, converted_curve):
    row, col = 0, 0
    while converted_curve[row][0] < height:
        row += 1
    x1 = float(converted_curve[row][0])
    y1 = float(converted_curve[row][1])
    x2 = float(converted_curve[row + 1][0])
    y2 = float(converted_curve[row + 1][1])

    return linear_func(x1, y1, x2, y2)


def linear_func(x1, y1, x2, y2):
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1

    def func(x):
        return m * x + b

    return func


def calc_spin_speeds(height, su8_type):
    if su8_type == '2000.5':
        su8_type = '2000_5'

    with open('assets/spin_curves/Spin_SU-8_' + su8_type + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        spin_speeds = [tuple([val for val in row]) for row in reader]

        spin_func = make_linear_func(height, spin_speeds)
        return spin_func(height)


def calc_sb_times(height, su8_type):
    curve_range = choose_resist_range(su8_type)

    with open('assets/sb_times/SB_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        sb_65_times = [(row[0], row[1]) for row in reader]
        sb_65_func = make_linear_func(height, sb_65_times)

        if len(reader[0]) == 3:
            sb_95_times = [(row[0], row[2]) for row in reader]
            sb_95_func = make_linear_func(height, sb_95_times)
            return sb_65_func(height), sb_95_func(height)

        return sb_65_func(height)


def calc_exp_energy(height, su8_type):
    curve_range = choose_resist_range(su8_type)

    with open('assets/exposure_energies/EE_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        exp_energies = [tuple([val for val in row]) for row in reader]

        ee_func = make_linear_func(height, exp_energies)
        return ee_func(height)


def calc_peb_time(height, su8_type):
    curve_range = choose_resist_range(su8_type)

    with open('assets/peb_times/PEB_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        peb_times = [tuple([val for val in row]) for row in reader]

        peb_func = make_linear_func(height, [peb_times])
        return peb_func(height)


def calc_dev_time(height, su8_type):
    curve_range = choose_resist_range(su8_type)

    with open('assets/development_times/DT_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        develop_times = [tuple([val for val in row]) for row in reader]

        develop_func = make_linear_func(height, [develop_times])
        return develop_func(height)


user_su8_type = input('Select SU-8 Type:')
user_height = input('Select desired channel height in µm:')

# Reads type of SU-8 user wants to use and selects correct files


print_values(user_height, user_su8_type)
