# prepareRLibs.r installs R library dependencies required by the detectors

options(repos=c(CRAN="http://cran.stat.sfu.ca/"))

# The arm package is needed to read CODA formatted output files from JAGS
install.packages('arm')
install.packages('plyr')
