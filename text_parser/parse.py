import pandas as pd
with open('text_parser/memoriasBras.txt', encoding="utf8") as f:
    lines = f.readlines()

lines = [line.replace("\n",'') for line in lines]

cap = 0
dic_cap={0:[]}
for i in range(len(lines)):
    if lines[i] == '<capitulo>':
        cap = cap+1
        dic_cap[cap] = []
    else:  
        dic_cap[cap].append(lines[i])

df = pd.DataFrame(columns = ['cap', 'line', 'content'],
                  )
print(df)
for cap in dic_cap:
    for line in range(0,len(dic_cap[cap])):
        df = df.append({'cap':cap, 'line':line, 'content':dic_cap[cap][line]}, ignore_index=True)
print(df)
df.to_csv('text_parser/memoriasBras.csv')
