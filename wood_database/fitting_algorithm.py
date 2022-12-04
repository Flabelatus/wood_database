def get_closest(value_1: int, value_2: int, target: int) -> int:
    """
    Find the closest value to the target number
    :param value_1: First value to check
    :param value_2: Second value to check
    :param target: The target number to evaluate
    :return: The closest of the values to the target
    """
    if target - value_1 >= value_2 - target:
        return value_2
    else:
        return value_1


def find_closest(array: list, length: int, target: int) -> int:
    """
    Find the closest value to the defined target from an array
    :param array: The array to search from
    :param length: The length of the array
    :param target: The value to search the closest member in the array
    :return: the closest member to the target from the array
    """
    if target <= array[0]:
        return array[0]
    if target >= array[-1]:
        return array[-1]

    low = 0
    high = length
    mid = 0
    while low < high:
        mid = low + high // 2

        if array[mid] == target:
            return array[mid]

        if target < array[mid]:
            if mid > 0 and target > array[mid - 1]:
                return get_closest(array[mid - 1], array[mid], target)
            high = mid

        else:
            if mid < length - 1 and target < array[mid + 1]:
                return get_closest(array[mid], array[mid + 1], target)

            low = mid + 1
    return array[mid]


def search(base_array: list, array_to_search_from: list) -> list:
    """
    Compare two arrays one as the base array, and the other as the searching target array. Find the closest members
    to the base array and return a new array. The new array is populated by the closest possible values from the
    searching array.

    :param base_array: The array to fit the closest members
    :param array_to_search_from: The array to search from to find the closest values to the ones existing in the base
        array
    :return: A new array that is populated with the members of the searching array that are closest to the base array
        members
    """
    found_closest_values = []
    hashset = set()

    # Copy the search array to not lose the original data from the array
    new_search_target_array = array_to_search_from.copy()

    while len(new_search_target_array) > len(array_to_search_from) / 2:
        for item in base_array:
            closest = find_closest(new_search_target_array, len(new_search_target_array), item)
            if closest in hashset:
                continue
            else:
                hashset.add(closest)
                found_closest_values.append(closest)
                new_search_target_array.remove(closest)

    return found_closest_values


def example():
    a = [65, 95, 95, 95, 95, 130, 130]
    b = [67, 68, 89, 91, 94, 96, 97, 122, 128, 129]

    print(f"Original base array: {a}\nOriginal searching array: {b}\nNew closest array: {search(a, b)}")


if __name__ == "__main__":
    example()
