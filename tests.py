class Curve():
    def __init__(self):
        self.yy = [1, 2]
        self.real = [1,3]
        self.img = [1]

        self.yy_saved = [1]
        self.real_saved = [1]
        self.img_saved = [1]

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __add__(self, other):
        "Adding to curves all fileds should be lists of the same length"
        result = Curve()
        result_vars = vars(result)
        other_vars = vars(other)

        for key, val in vars(self).items():
            #diffrent length allowed version
            # tmp = other_vars[key][:] #shallow copy
            # size_diff = len(val) - len(other_vars[key])
            # if size_diff != 0:
            
            #     zero_padding = [0] * abs(size_diff)
            #     if size_diff < 0:
            #         val = val + zero_padding
            #     else:
            #         tmp = other_vars[key] + zero_padding

            # result_vars[key] = [sum(x) for x in zip(val, tmp)]
            result_vars[key] = [sum(x) for x in zip(val, other_vars[key])]

        return result

    def var(self):
        print(vars(self))

    def var_edit(self, other):
        result = Curve()
        result_vars = vars(result)

        for key, val in vars(self).items():
            result_vars[key] = [sum(x) for x in zip(val, result_vars[key])]

        return result

a = Curve()
a.yy = [4,8]
a.var()
print(sum([a, Curve()]).var())
