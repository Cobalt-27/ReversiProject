with open('log3.txt','r') as f:
    raw=f.read()
    epoch=-1
    s=[]
    merged=[0 for _ in range(40)]
    for line in raw.split('\n'):
        if line.startswith('Epoch'):
            epoch+=1
            if len(s)!=0:
                print(s[-1])
            s.append(0)
            print('epoch '+ str(epoch))
        if line.startswith('score'):
            val=int(line[5:])
            # print(val)
            if val>0:
                s[epoch]+=1
            else:
                s[epoch]-=1
    for i,sc in enumerate(s):
        merged[i//5]+=sc
    print(merged)
        