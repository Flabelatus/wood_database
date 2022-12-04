def find_nearest(array, value):
    return array[min(range(len(array)), key=lambda i: abs(array[i] - value))]


def search(base_array, array_to_search_from):
    found_closest_values = []
    hashset = set()

    new_search_target_array = array_to_search_from.copy()

    while len(new_search_target_array) > len(array_to_search_from) / 2:
        for item in base_array:
            closest = find_nearest(new_search_target_array, item)
            if closest in hashset:
                continue
            else:
                hashset.add(closest)
                found_closest_values.append(closest)
                new_search_target_array.remove(closest)

    return found_closest_values
