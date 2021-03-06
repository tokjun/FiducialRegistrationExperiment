library(ggplot2)

# Plot error for each (translational or rotational) direction
plot.errors.direction <- function(r, errorType, xmin, xmax, ymin, ymax, title, xlabel, ylabel, xtick=10.0, ytick=1.0, xlegendpos=0.2, ylegendpos=0.8) {
    r2 <- r[r$ErrorType==errorType,]
    p <- ggplot(r2, aes(x=x, y=mean, group=Direction, color=Direction))
    #p <- p + geom_line() + geom_point()
    p <- p + geom_line(aes(linetype=Direction, colour=Direction)) + geom_point(aes(shape=Direction, colour=Direction), size=3)
    p <- p + labs(title=title, x=xlabel, y=ylabel)
    p <- p + theme_classic()
    p <- p + scale_color_manual(values=c('#0072BE','#DA5319', '#EEB220', '#7E2F8E','#77AD30', '#4DBFEF', '#A3142F'))
    p <- p + scale_x_continuous(breaks=seq(xmin,xmax,xtick), limits=c(xmin-2,xmax+2))
    p <- p + scale_y_continuous(breaks=seq(ymin,ymax,ytick), limits=c(ymin,ymax))
    p <- p + theme_bw() + theme(text = element_text(size=16), legend.key.size=unit(30, "pt"), legend.position=c(xlegendpos, ylegendpos))
    print(p)
}

# Plot error for each error type
plot.errors.type <- function(r, direction, xmin, xmax, ymin, ymax, title, xlabel, ylabel, xtick=10.0, ytick=1.0, xlegendpos=0.2, ylegendpos=0.8) {
    r2 <- r[r$Direction==direction,]
    p <- ggplot(r2, aes(x=x, y=mean, group=ErrorType, color=ErrorType))
    #p <- p + geom_line() + geom_point()
    p <- p + geom_line(aes(linetype=ErrorType, colour=ErrorType)) + geom_point(aes(shape=ErrorType, colour=ErrorType), size=3)
    p <- p + labs(title=title, x=xlabel, y=ylabel)
    p <- p + theme_classic()
    p <- p + scale_color_manual(values=c('#0072BE','#DA5319', '#EEB220', '#7E2F8E','#77AD30', '#4DBFEF', '#A3142F'))
    p <- p + scale_x_continuous(breaks=seq(xmin,xmax,xtick), limits=c(xmin-2,xmax+2))
    p <- p + scale_y_continuous(breaks=seq(ymin,ymax,ytick), limits=c(ymin,ymax))
    p <- p + theme_bw() + theme(text = element_text(size=16), legend.key.size=unit(30, "pt"), legend.position=c(xlegendpos, ylegendpos))
    print(p)
}

# Plot error (with error bar) for each (translational or rotational) direction
plot.errors.bars.direction <- function(r, errorType, xmin, xmax, ymin, ymax, title, xlabel, ylabel, xtick=10.0, ytick=1.0, xlegendpos=0.2, ylegendpos=0.8) {
    xmargin <- (xmax-xmin)*0.05
    r2 <- r[r$ErrorType==errorType,]
    p <- ggplot(r2, aes(x=x, y=mean, group=Direction, color=Direction))
    #p <- p + geom_line() + geom_point()
    p <- p + geom_line(aes(linetype=Direction, colour=Direction)) + geom_point(aes(shape=Direction, colour=Direction), size=3)
    #p <- p + geom_errorbar(aes(ymin=r2$mean-r2$sd, ymax=r2$mean+r2$sd), width=ebwidth, position=position_dodge(0.5))
    p <- p + geom_errorbar(aes(ymin=r2$mean-r2$sd, ymax=r2$mean+r2$sd, colour=Direction, linetype=Direction), width=ebwidth, position=position_dodge(0.1))
    p <- p + labs(title=title, x=xlabel, y=ylabel)
    p <- p + theme_classic()
    p <- p + scale_color_manual(values=c('#0072BE','#DA5319', '#EEB220', '#7E2F8E','#77AD30', '#4DBFEF', '#A3142F'))
    p <- p + scale_x_continuous(breaks=seq(xmin,xmax,xtick), limits=c(xmin-xmargin,xmax+xmargin))
    p <- p + scale_y_continuous(breaks=seq(ymin,ymax,ytick), limits=c(ymin,ymax))
    p <- p + theme_bw() + theme(text = element_text(size=16), legend.key.size=unit(30, "pt"), legend.position=c(xlegendpos, ylegendpos))
    print(p)
}

# Plot error (with error bar) for each (translational or rotational) direction
plot.errors.bars.type <- function(r, direction, xmin, xmax, ymin, ymax, title, xlabel, ylabel, xtick=10.0, ytick=1.0, xlegendpos=0.2, ylegendpos=0.8) {
    xmargin <- (xmax-xmin)*0.05
    ebwidth <- (xmax-xmin)*0.05
    r2 <- r[r$Direction==direction,]
    p <- ggplot(r2, aes(x=x, y=mean, group=ErrorType, color=ErrorType))
    #p <- p + geom_line() + geom_point()
    p <- p + geom_line(aes(linetype=ErrorType, colour=ErrorType)) + geom_point(aes(shape=ErrorType, colour=ErrorType), size=3)
    #p <- p + geom_errorbar(aes(ymin=r2$mean-r2$sd, ymax=r2$mean+r2$sd), width=ebwidth, position=position_dodge(0.5))
    p <- p + geom_errorbar(aes(ymin=r2$mean-r2$sd, ymax=r2$mean+r2$sd, colour=ErrorType, linetype=ErrorType), width=ebwidth, position=position_dodge(0.1))
    p <- p + labs(title=title, x=xlabel, y=ylabel)
    p <- p + theme_classic()
    p <- p + scale_color_manual(values=c('#0072BE','#DA5319', '#EEB220', '#7E2F8E','#77AD30', '#4DBFEF', '#A3142F'))
    p <- p + scale_x_continuous(breaks=seq(xmin,xmax,xtick), limits=c(xmin-xmargin,xmax+xmargin))
    p <- p + scale_y_continuous(breaks=seq(ymin,ymax,ytick), limits=c(ymin,ymax))
    p <- p + theme_bw() + theme(text = element_text(size=16), legend.key.size=unit(30, "pt"), legend.position=c(xlegendpos, ylegendpos))
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
    dR$ErrorType <- "Trans. Error: R"
    r <- dR
    dA <- aggregate.errors.x(data$dA, data[[by]])
    dA$Direction <- dirName
    dA$ErrorType <- "Trans. Error: A"
    r <- merge(r, dA, all=TRUE)
    dS <- aggregate.errors.x(data$dS, data[[by]])
    dS$Direction <- dirName
    dS$ErrorType <- "Trans. Error: S"
    r <- merge(r, dS, all=TRUE)    
    
    ThetaR <- aggregate.errors.x(data$ThetaR, data[[by]])
    ThetaR$Direction <- dirName
    ThetaR$ErrorType <- "Rot. Error: R"
    r <- merge(r, ThetaR, all=TRUE)    
    ThetaA <- aggregate.errors.x(data$ThetaA, data[[by]])
    ThetaA$Direction <- dirName
    ThetaA$ErrorType <- "Rot. Error: A"
    r <- merge(r, ThetaA, all=TRUE)    
    ThetaS <- aggregate.errors.x(data$ThetaS, data[[by]])
    ThetaS$Direction <- dirName
    ThetaS$ErrorType <- "Rot. Error: S"
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


aggregate.errors.trefre <- function(data, by, dirName) {

    FRE <- aggregate.errors.x(data$FRE, data[[by]])
    FRE$Direction <- dirName
    FRE$ErrorType <- "FRE"
    r <- FRE
    TRE <- aggregate.errors.x(data$TRE, data[[by]])
    TRE$Direction <- dirName
    TRE$ErrorType <- "TRE"
    r <- merge(r, TRE, all=TRUE)

    return (r)
}


#setwd('/home/develop/Dropbox/Experiments/Canon/FiducialTest')
setwd('/Users/junichi/Dropbox/Experiments/Canon/FiducialTest')

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

xmin <- 0
xmax <- 150
ymin <- -5
ymax <- 5

trans <- errorData[errorData$BlockTilt==0&errorData$BlockRot==0&errorData$FiducialRot==0,]
transR <- trans[trans$A==10&trans$S==0,]
tR <- aggregate.errors.all(transR, "R", "R")
transA <- trans[trans$R==0&trans$S==0,]
tA <- aggregate.errors.all(transA, "A", "A")
tA$x <- tA$x-10.0 # calibrate to zero
transS <- trans[trans$R==0&trans$A==10,]
tS <- aggregate.errors.all(transS, "S", "S")
transErrors <- rbind(tR, tA, tS)

## RMS plot
pdf("trans-RMS.pdf")
plot.errors.direction(transErrors, "RMS", xmin, xmax, ymin, ymax, "Root Mean Square Errors with R/A/S Translations", "Translation (mm)", "RMS Error (mm)")
dev.off()


transErrorsNoRMS <- transErrors[transErrors$ErrorType!="RMS",]

## Plot for R translation
pdf("Translation-R.pdf")
plot.errors.bars.type(transErrorsNoRMS, "R", 0, 100, ymin, ymax, "Translational/Rotational Errors with R-Translation", "R-Translation (mm)", "Errors (mm for Translation / Deg. for Rotation)")
dev.off()

## Plot for A translation
pdf("Translation-A.pdf")
plot.errors.bars.type(transErrorsNoRMS, "A", 0, 40, ymin, ymax, "Translational/Rotational Errors with A-Translation", "A-Translation (mm)", "Errors (mm for Translation / Deg. for Rotation)")
dev.off()

## Plot for S translation
pdf("Translation-S.pdf")
plot.errors.bars.type(transErrorsNoRMS, "S", 0, 150, ymin, ymax, "Translational/Rotational Errors with S-Translation", "S-Translation (mm)", "Errors (mm for Translation / Deg. for Rotation)")
dev.off()

xmin <- 0
xmax <- 270
ymin <- -6
ymax <- 6

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
plot.errors.direction(rotErrors, "RMS", xmin, xmax, ymin, ymax, "Root Mean Square Errors with Rotations About R/A/S-Axes", "Rotation (Deg.)", "RMS Error (mm)", 30.0, 1.0)
dev.off()

rotErrorsNoRMS <- rotErrors[rotErrors$ErrorType!="RMS",]

## Plot for R rotation
pdf("Rotation-R.pdf")
plot.errors.bars.type(rotErrorsNoRMS, "RotR", 0, 90, ymin, ymax, "Translational/Rotational Errors with Rotation About R-Axis", "R-Rotation (Deg.)", "Errors (mm for Translation / Deg. for Rotation)", 30.0, 1.0)
dev.off()

## Plot for A rotation
pdf("Rotation-A.pdf")
plot.errors.bars.type(rotErrorsNoRMS, "RotA", 0, 270, ymin, ymax, "Translational/Rotational Errors with Rotation About A-Axis", "A-Rotation (Deg.)", "Errors (mm for Translation / Deg. for Rotation)", 30.0, 1.0)
dev.off()

## Plot for S rotation
pdf("Rotation-S.pdf")
plot.errors.bars.type(rotErrorsNoRMS, "RotS", 0, 90, ymin, ymax, "Translational/Rotational Errors with Rotation About S-Axis", "S-Rotation (Deg.)", "Errors (mm for Translation / Deg. for Rotation)", 30.0, 1.0)
dev.off()


xmin <- 0
xmax <- 270
ymin <- -1
ymax <- 11

## TRE / FRE
trefreTR <- aggregate.errors.trefre(transR, "R", "R")
trefreTA <- aggregate.errors.trefre(transA, "A", "A")
trefreTA$x <- trefreTA$x-10.0 # calibrate to zero
trefreTS <- aggregate.errors.trefre(transS, "S", "S")
transTREFRE <- rbind(trefreTR, trefreTA, trefreTS)

## Plot for R translation
pdf("TREFRE-R.pdf")
plot.errors.bars.type(transTREFRE, "R", 0, 100, ymin, ymax, "FRE/TRE with R-Translation", "R-Translation (mm)", "FRE/TRE (mm)")
dev.off()

## Plot for A translation
pdf("TREFRE-A.pdf")
plot.errors.bars.type(transTREFRE, "A", 0, 40, ymin, ymax, "FRE/TRE with A-Translation", "A-Translation (mm)", "FRE/TRE (mm)")
dev.off()

## Plot for S translation
pdf("TREFRE-S.pdf")
plot.errors.bars.type(transTREFRE, "S", 0, 150, ymin, ymax, "FRE/TRE with S-Translation", "S-Translation (mm)", "FRE/TRE (mm)")
dev.off()

trefreRR <- aggregate.errors.trefre(rotR, "BlockTilt", "RotR")
trefreRS <- aggregate.errors.trefre(rotS, "BlockTilt", "RotS")
trefreRA <- aggregate.errors.trefre(rotA, "FiducialRot", "RotA")
rotTREFRE <- rbind(trefreRR, trefreRA, trefreRS)

## Plot for R rotation
pdf("TREFRE-RotR.pdf")
plot.errors.bars.type(rotTREFRE, "RotR", 0, 90, ymin, ymax, "FRE/TRE with Rotation About R-Axis", "R-Rotation (Deg.)", "FRE/TRE (mm)", 30.0, 1.0)
dev.off()

## Plot for A rotation
pdf("TREFRE-RotA.pdf")
plot.errors.bars.type(rotTREFRE, "RotA", -0, 270, ymin, ymax, "FRE/TRE with Rotation About A-Axis", "A-Rotation (Deg.)", "FRE/TRE (mm)", 30.0, 1.0)
dev.off()

## Plot for S rotation
pdf("TREFRE-RotS.pdf")
plot.errors.bars.type(rotTREFRE, "RotS", 0, 90, ymin, ymax, "FRE/TRE with Rotation About S-Axis", "S-Rotation (Deg.)", "FRE/TRE (mm)", 30.0, 1.0)
dev.off()


### Statistics
print(sprintf("Number of images: %d",  nrow(errorData)))
print(sprintf("Average process time: %f +/- %f", mean(errorData$ProcTime), sd(errorData$ProcTime)))
print(sprintf("Average wall time: %f +/- %f", mean(errorData$WallTime), sd(errorData$WallTime)))
print(sprintf("Fiducial detection rate: %f %%", sum(errorData$FiducialDetected)/(nrow(errorData)*8) * 100))
print(sprintf("Overall FRE: %f +/- %f", mean(errorData$FRE), sd(errorData$FRE)))
print(sprintf("Overall TRE (@ 150 mm): %f +/- %f", mean(errorData$TRE), sd(errorData$TRE)))
