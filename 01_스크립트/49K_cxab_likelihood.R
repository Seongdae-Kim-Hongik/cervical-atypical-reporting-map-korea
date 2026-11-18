# 49K — CXAB 우도 비교 보조(2026-11-13, 47K 복제). 강제통제 5 + BYM2(593) + RW1 + 연도 iid, offset = E_std(std3 패널 E, 여자 14연령 간접표준화).
#  Poisson · NB · 이항(Ntrials=수검자, offset=logit(E/수검자)) · 베타이항 · Poisson+관측 iid 5종: WAIC·DIC·−Σlog CPO. 0칸이 없어(0/3206) ZIP·ZINB 대신 이항 계열(판정 비율 자료)로 둔다.
#  사용(01_스크립트/에서): Rscript 49K_cxab_likelihood.R   산출: 04_분석/CXAB/results_std3/S49K_likelihood.csv
suppressPackageStartupMessages({library(INLA);library(jsonlite)})
inla.setOption(num.threads="1:1")
D<-file.path("..","04_분석","CXAB");OUT<-file.path(D,"results_std3");dir.create(OUT,showWarnings=FALSE)
S<-fromJSON(file.path(D,"config_CXAB_std3.json"))
DD<-read.csv(file.path(D,"panel_CXAB_std3.csv"),fileEncoding="UTF-8-BOM",stringsAsFactors=FALSE)
g<-inla.read.graph(file.path(D,"graph_593.graph"))
suppressPackageStartupMessages(library(sf))
SHP<-Sys.getenv("ST_SHP",file.path(normalizePath(file.path(dirname(sub("--file=","",grep("--file=",commandArgs(),value=TRUE))),"..")),"data","boundary","final.shp"))
G<-st_read(SHP,quiet=TRUE);G$region<-enc2utf8(G$region);DD$fbd_region<-enc2utf8(DD$fbd_region);stopifnot(g$n==nrow(G),all(DD$fbd_region%in%G$region))
DD$area<-match(DD$fbd_region,G$region)   # 81과 같은 노드 순서(final.shp)
DD$time<-DD$year-min(DD$year)+1;DD$yiid<-DD$time;DD$obs<-seq_len(nrow(DD))
pc<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)),phi=list(prior="pc",param=c(0.5,2/3)));pcp<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)))
base<-paste("cases ~ 1 +",paste(sprintf("`%s`",S$forced),collapse="+"),
  "+ f(area,model='bym2',graph=g,scale.model=TRUE,constr=TRUE,hyper=pc) + f(time,model='rw1',scale.model=TRUE,hyper=pcp) + f(yiid,model='iid',hyper=pcp)")
DD$lo<-qlogis(DD$E/DD$offset)
fit<-function(fam,extra=""){f<-as.formula(paste(base,extra));t0<-Sys.time()
  bin<-fam%in%c("binomial","betabinomial")
  if(bin) f<-update(f,.~.+offset(lo))
  args<-list(formula=f,family=fam,data=DD,control.fixed=list(mean=0,prec=4,mean.intercept=0,prec.intercept=0.001),
    control.compute=list(waic=TRUE,dic=TRUE,cpo=TRUE,config=FALSE),control.predictor=list(compute=TRUE,link=1),
    control.inla=list(control.vb=list(emergency=50)))
  if(bin) args$Ntrials<-DD$offset else args$E<-DD$E
  m<-do.call(inla,args)
  cpo<-m$cpo$cpo;nf<-sum(m$cpo$failure>0,na.rm=TRUE);hp<-m$summary.hyperpar
  data.frame(likelihood=paste0(fam,ifelse(extra=="","","+obs_iid")),WAIC=round(m$waic$waic,1),DIC=round(m$dic$dic,1),neg_logscore=round(-sum(log(cpo),na.rm=TRUE),1),cpo_fail=nf,
    overdispersion=ifelse(fam=="nbinomial",round(hp[grep("size",rownames(hp)),"mean"],2),ifelse(fam=="betabinomial",signif(hp[grep("overdispersion",rownames(hp)),"mean"],3),NA)),
    observed_zeros=sum(DD$cases==0),minutes=round(as.numeric(difftime(Sys.time(),t0,units="mins")),2))}
R<-rbind(fit("poisson"),fit("nbinomial"),fit("binomial"),fit("betabinomial"),fit("poisson","+ f(obs,model='iid',hyper=pcp)"))
write.csv(R,file.path(OUT,"S49K_likelihood.csv"),row.names=FALSE);print(R)
