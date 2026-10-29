import random


def partition(arr, low, high):
    r = random.randint(low, high)
    arr[r], arr[high] = arr[high], arr[r]
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quicksort(arr, low, high):
    if low < high:
        p = partition(arr, low, high)
        quicksort(arr, low, p - 1)
        quicksort(arr, p + 1, high)


arr = [10, 7, 8, 9, 1, 5, 3]
quicksort(arr, 0, len(arr) - 1)
print(arr)
