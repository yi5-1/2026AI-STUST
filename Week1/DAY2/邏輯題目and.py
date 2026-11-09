"""
🛒 場景：超商買珍奶（滿 18 歲 且 有帶錢）
假設今天店家規定，
買某款微醺珍奶必須同時滿足兩個條件：年齡夠、口袋有錢。
"""
age = 20
has_money = True
男的 = True
# 兩個條件都必須是 True
if (age >= 18 and has_money == True and 男的==True) :
    print("恭喜！成功買到珍奶 🧋")
else:
    print("條件不符，不能買喔！")