# 49P — CXAB 역방향 사후 검정(결과 본 뒤, 15 역방향 절차 2단계): 신체활동 3지표 각각 단독 + 강제통제, 중강도 + 같은 축(걷기·체육시설) 제외 전 가설 모형. NB, 주모형과 같은 랜덤효과(2026-11-13, 47K 복제). 강제통제 5 + BYM2(593) + RW1 + 연도 iid, offset = E_std(std3 패널 E, 여자 14연령 간접표준화).
#  Poisson · NB · 이항(Ntrials=수검자, offset=logit(E/수검자)) · 베타이항 · Poisson+관측 iid 5종: WAIC·DIC·−Σlog CPO. 0칸이 없어(0/3206) ZIP·ZINB 대신 이항 계열(판정 비율 자료)로 둔다.
#  사용(01_스크립트/에서): Rscript 49K_cxab_likelihood.R   산출: 04_분석/CXAB/results_std3/S49P_pa_reverse.csv
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
fitv<-function(v,lab){f<-as.formula(paste(base,"+",paste(sprintf("`%s`",v),collapse="+")))
  m<-inla(f,family="nbinomial",data=DD,E=DD$E,control.fixed=list(mean=0,prec=4,mean.intercept=0,prec.intercept=0.001),control.compute=list(waic=TRUE),control.inla=list(control.vb=list(emergency=50)))
  fx<-m$summary.fixed;r<-data.frame(model=lab,cov=gsub("`","",rownames(fx)),IRR=round(exp(fx$mean),3),lo=round(exp(fx[["0.025quant"]]),3),hi=round(exp(fx[["0.975quant"]]),3),WAIC=round(m$waic$waic,1));r$cred<-r$lo>1|r$hi<1;r[r$cov!="(Intercept)",]}
PA<-c("walking_practice_rate","moderate_pa_rate","public_sports_facilities_per_100k")
HYP<-S$sets_after_vif$S1_narrative_full
R<-rbind(do.call(rbind,lapply(PA,function(v)fitv(v,paste0("alone_",v)))),fitv(setdiff(HYP,c("walking_practice_rate","public_sports_facilities_per_100k")),"moderate_without_same_axis"),fitv(setdiff(HYP,PA),"no_pa"))
write.csv(R,file.path(OUT,"S49P_pa_reverse.csv"),row.names=FALSE);print(R[R$cov%in%c(PA,"crude_divorce_rate","foreign_residents_per_1000"),])
