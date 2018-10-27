import csv


# Reads type of SU-8 user wants to use and selects correct files
def print_values(channel_height, resist_type):
    channel_height = float(channel_height)
    resist_type = float(resist_type)
    spin_speed = calc_spin_speeds(channel_height, resist_type)
    sb_times = calc_sb_times(channel_height, resist_type)
    exp_energy = calc_exp_energy(channel_height, resist_type)
    peb_times = calc_peb_time(channel_height, resist_type)
    dev_time = calc_dev_time(channel_height, resist_type)

    print('Spin coat at v1 = 300 rpm, a1 = 100 rpm/s and v2 = ' + str(spin_speed) + ', a2 = 300 rpm/s.')
    if len(sb_times) == 2:
        print('Perform Soft Bake for ' + str(sb_times[0]) + ' minutes at 65C and ' + str(sb_times[1]) + ' minutes at 95C.')
    else:
        print('Perform Soft Bake for ' + str(sb_times) + ' minutes.')
    print('Expose surface to ' + str(exp_energy) + ' mJ/cm^2.')
    if len(peb_times) == 2:
        print('Perform Post Exposure Bake for ' + str(peb_times[0]) + ' minutes at 65C and '
              + str(peb_times[1]) + ' minutes at 95C.')
    else:
        print('Perform Post Exposure Bake for ' + str(peb_times) + ' minutes.')
    print('Develop wafer in SU-8 Developer for ' + str(dev_time) + ' minutes.')


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


# Checks to see whether or not this curve slopes upwards or downwards. This could cause problems
# if non-monotonic data sets are added in the future.
def is_upward_slope(converted_curve):

    y_one = float(converted_curve[0][1])
    y_two = float(converted_curve[1][1])

    return y_two > y_one


# Uses a HOF to produce the correct procedure for finding relevant section of the curve
# TODO: Add error-catching to catch people who specify a height outside the range
def find_flanking_points_maker(height, upward_slope):

    def find_flanking_points(converted_curve):
        row, col = 0, 0
        if upward_slope:
            while float(converted_curve[row][0]) < height:
                row += 1
        else:
            while float(converted_curve[row][0]) > height:
                row += 1
        # For the case where the last value in the set is your desired height
        if row == len(converted_curve) - 1 and converted_curve[row] == height:
            x1 = float(converted_curve[row - 1][0])
            y1 = float(converted_curve[row - 1][1])
            x2 = float(converted_curve[row][0])
            y2 = float(converted_curve[row][1])
        else:
            x1 = float(converted_curve[row][0])
            y1 = float(converted_curve[row][1])
            x2 = float(converted_curve[row + 1][0])
            y2 = float(converted_curve[row + 1][1])

        return (x1, y1), (x2, y2)

    return find_flanking_points


# Using HOFs to return a suitable linear function for any input range
def make_linear_func(height, converted_curve):
    flanking_point_finder = find_flanking_points_maker(height, is_upward_slope(converted_curve))
    point_one = flanking_point_finder(converted_curve)[0]
    point_two = flanking_point_finder(converted_curve)[1]

    return linear_func(point_one[0], point_one[1],  point_two[0], point_two[1])


def linear_func(x1, y1, x2, y2):
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1

    def func(x):
        return m * x + b

    return func


def calc_spin_speeds(height, su8_type):
    if su8_type == 2000.5:
        su8_type_str = '2000_5'
    else:
        su8_type_str = str(int(su8_type))

    with open('assets/spin_curves/Spin_SU-8_' + su8_type_str + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        spin_speeds = [tuple([val for val in row]) for row in reader]

        spin_func = make_linear_func(height, spin_speeds)
        return spin_func(height)


def calc_sb_times(height, su8_type):
    curve_range = choose_resist_range(su8_type)

    with open('assets/sb_times/SB_SU-8_' + curve_range + '.csv', mode='r') as csvfile:

        reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        sb_both_temps = [tuple([col for col in row]) for row in reader]

        num_cols = len(sb_both_temps[0])
        sb_65_times = [(row[0], row[1]) for row in sb_both_temps]
        sb_65_func = make_linear_func(height, sb_65_times)

        if num_cols == 3:
            sb_95_times = [(row[0], row[2]) for row in sb_both_temps]
            sb_95_func = make_linear_func(height, sb_95_times)
            return sb_65_func(height), sb_95_func(height)

        return sb_65_func(height)


def calc_exp_energy(height, su8_type):
    curve_range = choose_resist_range(su8_type)

    with open('assets/exposure_energies/EE_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        exp_energies = [tuple([float(val) for val in row]) for row in reader]

        ee_func = make_linear_func(height, exp_energies)
        return ee_func(height)


def calc_peb_time(height, su8_type):
    curve_range = choose_resist_range(su8_type)

    with open('assets/peb_times/PEB_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        #  fix the bit I was stuck on in calc_sb_time
        reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        peb_both_temps = [tuple([col for col in row]) for row in reader]
        num_cols = len(peb_both_temps[0])

        peb_65_times = [(row[0], row[1]) for row in peb_both_temps]
        peb_65_func = make_linear_func(height, peb_65_times)

        if num_cols == 3:
            peb_95_times = [(row[0], row[2]) for row in peb_both_temps]
            peb_95_func = make_linear_func(height, peb_95_times)
            return peb_65_func(height), peb_95_func(height)

        return peb_65_func(height)


def calc_dev_time(height, su8_type):
    curve_range = choose_resist_range(su8_type)

    with open('assets/development_times/DT_SU-8_' + curve_range + '.csv', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        develop_times = [tuple([float(val) for val in row]) for row in reader]

        develop_func = make_linear_func(height, develop_times)
        return develop_func(height)


user_su8_type = input('Select SU-8 Type:')
user_height = float(input('Select desired channel height in µm:'))


print_values(user_height, user_su8_type)
