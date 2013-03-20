#library('plyr')

timings=read.csv('timings.csv', header=FALSE)

data=round(timings$V1*1000)
N=length(data)

cat('N <-', N, "\n", file="data.txt")
cat('timings <- c(', paste(data, collapse=','), ")\n", file='data.txt', append=TRUE)
