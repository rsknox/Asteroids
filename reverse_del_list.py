a = [1, 2, 3, 4, 1, 2, 3, 4, 4, 3, 2, 1, 0]
#b = list(a)
#print('len: ', len(b))
for i in range(len(a)-1, -1, -1):
    print('i: ', i, 'a[i]: ', a[i])
    if a[i] == 4:
        print(a[i])
        del a[i]
print(a)

print('---- a second way ------------')

a = [1, 2, 3, 4, 1, 2, 3, 4, 4, 3, 2, 1, 0]
j = len(a) - 1
for i in range(len(a)):
    print('i:,', i, 'j: ', j, 'a[j]: ', a[j])
    if a[j] == 2:
        print('deleting a[j]: ', a[j])
        del a[j]
    j = j - 1
    
print(a)
