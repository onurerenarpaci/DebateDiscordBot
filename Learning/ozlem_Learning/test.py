import csv

teamdict =	{
  "A": ["1","2","3"],
  "B": ["4","5","6"],
  "C": ["7","8","9"],
  "D": ["10","11","12"],
  "E": ["13","14","15"]
}

adj_dict =	{
  "A": ["11","22","33"],
  "B": ["44","55","66"],
  "C": ["77","88","99"],
  "D": ["100","111","122"],
  "E": ["133","144","155"]
}

final_dict = teamdict.copy()
for x in final_dict:
    final_dict[x]= teamdict[x] + (adj_dict[x])
    #print(teamdict[x])
"""
csvval=csv.writer(open("deneme.csv","w"))

csvval.writerow(['deneme 321']+['Test 321'])


print("-----")
sorted_dic={}
for i in sorted (final_dict) : 
    sorted_dic[i]=final_dict[i]
"""
csvval=csv.writer(open("deneme4.csv","w"))
odax=[]
for x,y in teamdict.items():
    odax.append(x)
    for a in y:
        odax.append(a)
    csvval.writerows([odax])
    odax.clear()

print("----")

