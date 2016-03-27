library(ggplot2)

plot.errors <- function(r, errorType, ymin, ymax, title) {
    r2 <- r[r$ErrorType==errorType,]
    p <- ggplot(r2, aes(x=x, y=mean, group=Direction, color=Direction)) + geom_line() + geom_point() + labs(title=title, x="Translation (mm)", y = "Error (mm)") + theme_classic() + scale_color_manual(values=c('#FFA0A0','#A0FFA0', '#A0A0FF'))
    print(p)
}

plot.errors.error.bars <- function(r, errorType, ymin, ymax, title) {
    r2 <- r[r$ErrorType==errorType,]
    p <- ggplot(r2, aes(x=x, y=mean, group=Direction, color=Direction)) + geom_line() + geom_point() + geom_errorbar(aes(ymin=r2$mean-r2$sd, ymax=r2$mean+r2$sd), width=2,position=position_dodge(0.5)) + labs(title=title, x="Translation (mm)", y = "Error (mm)") + theme_classic() + scale_color_manual(values=c('#FFA0A0','#A0FFA0', '#A0A0FF'))
    print(p)
}

aggregate.errors.x <- function(x, by) {
    m <- aggregate(x, list(by), mean)
    s <- aggregate(x, list(by), sd)
    r <- data.frame(x=m$Group.1, mean=m$x, sd=s$x)
    return (r)
}

aggregate.errors.all <- function(data, by, dirName) {

    dR <- aggregate.errors.x(data$dR, data[[by]])
    dR$Direction <- dirName
    dR$ErrorType <- "dR"
    r <- dR
    dA <- aggregate.errors.x(data$dA, data[[by]])
    dA$Direction <- dirName
    dA$ErrorType <- "dA"
    r <- merge(r, dA, all=TRUE)
    dS <- aggregate.errors.x(data$dS, data[[by]])
    dS$Direction <- dirName
    dS$ErrorType <- "dS"
    r <- merge(r, dS, all=TRUE)    
    
    ThetaR <- aggregate.errors.x(data$ThetaR, data[[by]])
    ThetaR$Direction <- dirName
    ThetaR$ErrorType <- "ThetaR"
    r <- merge(r, ThetaR, all=TRUE)    
    ThetaA <- aggregate.errors.x(data$ThetaA, data[[by]])
    ThetaA$Direction <- dirName
    ThetaA$ErrorType <- "ThetaA"
    r <- merge(r, ThetaA, all=TRUE)    
    ThetaS <- aggregate.errors.x(data$ThetaS, data[[by]])
    ThetaS$Direction <- dirName
    ThetaS$ErrorType <- "ThetaS"
    r <- merge(r, ThetaS, all=TRUE)    
    
    sqre <- data$dR^2 + data$dA^2 + data$dS^2
    RMS <- aggregate.errors.x(sqre, data[[by]])
    RMS$mean <- sqrt(RMS$mean)
    RMS$sd <- sqrt(RMS$sd)
    RMS$Direction <- dirName
    RMS$ErrorType <- "RMS"
    r <- merge(r, RMS, all=TRUE)    

    return (r)
}


setwd('/home/develop/Projects/Canon/FiducialTest')
errorData1119 <- read.csv('Error-2015-11-19.csv')
errorData1119$date <- 1119

errorData1127 <- read.csv('Error-2015-11-27.csv')
errorData1127$date <- 1127

errorData1204 <- read.csv('Error-2015-12-04.csv')
errorData1204$date <- 1204

errorData1210 <- read.csv('Error-2015-12-10.csv')
errorData1210$date <- 1210

errorData <- rbind(errorData1119, errorData1127, errorData1204, errorData1210)

# Plot R, A, and S errors vs R-translation
errorData$R <- (-errorData$R)
errorData$S <- (-errorData$S)

tmin <- -8
tmax <- 8

trans <- errorData[errorData$BlockTilt==0&errorData$BlockRot==0&errorData$FiducialRot==0,]
transR <- trans[trans$A==10&trans$S==0,]
tR <- aggregate.errors.all(transR, "R", "R")
transA <- trans[trans$R==0&trans$S==0,]
tA <- aggregate.errors.all(transA, "A", "A")
transS <- trans[trans$R==0&trans$A==10,]
tS <- aggregate.errors.all(transS, "S", "S")

transErrors <- rbind(tR, tA, tS) 
pdf("trans-RMS.pdf")
plot.errors(transErrors, "RMS", tmin, tmax, 'Root Mean Square Errors')
dev.off()



##BlockRot=0 : facing door of MR room
rot <- errorData[errorData$R==0&errorData$A==10&errorData$S==0,]
rotR <- rot[errorData$BlockRot==0&errorData$FiducialRot==0,]
rR <- aggregate.errors.all(rotR, "BlockTilt", "RotR")
rotS <- rot[errorData$BlockRot==90&errorData$FiducialRot==0,]
rS <- aggregate.errors.all(rotS, "BlockTilt", "RotS")
rotA <- rot[errorData$BlockRot==0,]
rA <- aggregate.errors.all(rotA, "FiducialRot", "RotA")

rotErrors <- rbind(rR, rA, rS) 
pdf("rot-RMS.pdf")
plot.errors(rotErrors, "RMS", tmin, tmax, 'Root Mean Square Errors')
dev.off()

