library(arm)
library(coda)
library('plyr')

res1 = read.coda("obfsproxy/CODAchain1.txt", "obfsproxy/CODAindex.txt")
res2 = read.coda("SSL/CODAchain1.txt", "SSL/CODAindex.txt")
res3 = read.coda("Dust/CODAchain1.txt", "Dust/CODAindex.txt")

write.table(res1, 'obfsproxy.csv', col.names=FALSE, row.names=FALSE, sep=',')
write.table(res2, 'SSL.csv', col.names=FALSE, row.names=FALSE, sep=',')
write.table(res3, 'Dust.csv', col.names=FALSE, row.names=FALSE, sep=',')

