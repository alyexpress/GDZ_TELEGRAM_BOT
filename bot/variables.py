from pprint import pprint
from datetime import date

class Varibles:
    def __init__(self):
        self.mem = {}
        self.nums = {}
    def set(self, user, varible, value):
        if user in self.mem: self.mem[user][varible] = value
        else: self.mem[user] = {varible: value}
    def get(self, user, varible):
        try: return self.mem[user][varible]
        except: return False
    def reset(self, user, *vars):
        vars = vars if vars else ['item', '_num']
        for var in vars: self.set(user, var, None)
    def set_ad(self, user):
        if not self.get(user, 'ad'):
            self.set(user, 'ad', 5)
    def ad(self, user):
        self.set_ad(user)
        self.mem[user]['ad'] -= 1
        if self.get(user, 'ad'): return False
        else:
            self.set_ad(user)
            return True
    def set_nums(self, item, nums, _num=None):
        _num = _num + ":" if _num else ""
        nums = _num + ",".join(nums)
        if item not in self.nums:
            self.nums[item] = {nums: [1, date.today()]}
        else:
            if nums not in self.nums[item]:
                self.nums[item][nums] = [1, date.today()]
            else: self.nums[item][nums][0] += 1
    def get_nums(self, item):
        try: nums = list(self.nums[item].items())
        except: return []
        nums.sort(key=lambda x: (x[1][1], x[1][0]), reverse=True)
        if len(nums) > 5:
            for i in nums[5:]: del self.nums[item][i[0]]
        return list(map(lambda x: x[0], nums[:3]))
    def print(self):
        pprint(self.mem)
        pprint(self.nums)