"""Heapsort implementation for the CSE 565 unit testing project."""
class heap:
    def __init__(self, arr=[]):
        self.arr = list(arr)


    def swap(self, endex):
        if endex > 1:
            temp = self.arr[0]
            self.arr[0] = self.arr[endex-1]
            self.arr[endex-1] = temp


    def build_max_heap(self, i, endex):
        # build max heap from the array until endex
        if i < endex:
            l = 2 * i + 1
            r = 2 * i + 2
            self.build_max_heap(l, endex)
            self.build_max_heap(r, endex)
            if l < endex:
                if self.arr[l] > self.arr[i]:
                    temp = self.arr[i]
                    self.arr[i] = self.arr[l]
                    self.arr[l] = temp
            if r < endex:
                if self.arr[r] > self.arr[i]:
                    temp = self.arr[i]
                    self.arr[i] = self.arr[r]
                    self.arr[r] = temp


    def heapify(self):
        for i in range(len(self.arr)):
            self.build_max_heap(0, len(self.arr)-i)
            self.swap(len(self.arr)-i)
            



if __name__ == "__main__":
    sample = [12, 11, 13, 5, 6, 7]
    h = heap(sample)
    h.heapify()
    print(h.arr)
    