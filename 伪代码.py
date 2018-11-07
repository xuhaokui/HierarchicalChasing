# -*- coding: utf-8 -*-
"""
Created on Tue Sep 04 21:41:19 2018

@author: Edward Coen
"""

class prior():  
    
    def __init__(self, all_table_partion_list):
        self.all_table_partion_list = all_table_partion_list
    
    def cal_renomalize_parameter(self, table_partion):
        return 1/((1 - scipy.special.gamma(GAMMA) * GAMMA * scipy.special.gamma(np.array(table_partion).sum()) / scipy.special.gamma(np.array(table_partion).sum() + GAMMA)) * len(list(set(itertools.permutations(np.array(table_partion)))))) 
        
    def cal_probability_table_partion(self, table_partion):
#        print table_partion
#        print reduce(op.mul, map(scipy.special.gamma, np.array(table_partion))) * scipy.special.gamma(GAMMA) * pow(GAMMA, len(table_partion)) / scipy.special.gamma(np.array(table_partion).sum() + GAMMA)
        return reduce(op.mul, map(scipy.special.gamma, np.array(table_partion))) * scipy.special.gamma(GAMMA) * pow(GAMMA, len(table_partion)) / scipy.special.gamma(np.array(table_partion).sum() + GAMMA)
            
    def cal_permutation_table_partion(self, table_partion):
        return list(set(list(itertools.permutations(table_partion))))
    
    def cal_all_combination_guest(self, permutation_table_partion): 
        return reduce(op.add, map(self.cal_permutation_combination_guest, permutation_table_partion))
        
    def cal_permutation_combination_guest(self, table_partion):
        self.guest_left = np.array(table_partion).sum()
        return reduce(op.mul, map(self.cal_combination_guest, table_partion))
        
    def cal_combination_guest(self, table_guest_num):
        combination_num = round(comb(self.guest_left - 1, table_guest_num - 1))
        self.guest_left = self.guest_left - table_guest_num
        return combination_num

    def cal_prior_probability(self, table_partion_list):
        probability_table_partion = map(self.cal_probability_table_partion, table_partion_list[1:])
        permutation_table_partion = map(self.cal_permutation_table_partion, table_partion_list[1:])
        all_combination_guest = map(self.cal_all_combination_guest, permutation_table_partion)
        renomalize_parameter = map(self.cal_renomalize_parameter, table_partion_list[1:])
#        print 'ttt', all_combination_guest, renomalize_parameter
#        print reduce(op.mul, np.array(probability_table_partion)*np.array(all_combination_guest)*np.array(renomalize_parameter))
        return reduce(op.mul, np.array(probability_table_partion)*np.array(all_combination_guest)*np.array(renomalize_parameter))
        
    def __call__(self):
        return map(self.cal_prior_probability, self.all_table_partion_list)
    
    
这是我用来算prior的，其中枚举树的种类相关的主要是21和22行的函数（比如一个table_partition = [321121111],表示先分为321,随后3分为12,2分为11,以及3中的2再分为11。
                                                              此时考虑所有位置,321的全排列，如132,213,231等等，再乘以12的排列，乘以11的全排列和11的全排列）
                                                              可以得到[321121111]这种树等价的所有树的可能）
但是【321121111】是6客体的ncrp产生的一种原型树，有多少种原型树我没有用公式写过，是ncrp产生跑了100000次以后把所有重复树合并后的1种，因为跑了很多次，所以我认为
枚举完成了，事实表明6客体的原型树有33种（100000次合并就这33种），这33种原型树(因为ncrp“左倾”)再根据上面的def可以得到每种树下的等价树的数目，一共有140种左右。