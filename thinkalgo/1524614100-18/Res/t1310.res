BEGIN_FUNCTION_MAP
	.Func,주식당일전일분틱조회(t1310),t1310,attr,block,headtype=A;
	BEGIN_DATA_MAP
	t1310InBlock,기본입력,input;
	begin
		당일전일구분,daygb,daygb,char,1;
		분틱구분,timegb,timegb,char,1;
		단축코드,shcode,shcode,char,6;
		종료시간,endtime,endtime,char,4;
		시간CTS,cts_time,cts_time,char,10;
	end
	t1310OutBlock,출력,output;
	begin
		시간CTS,cts_time,cts_time,char,10;
	end
	t1310OutBlock1,출력1,output,occurs;
	begin
		시간,chetime,chetime,char,10;
		현재가,price,price,long,8;
		전일대비구분,sign,sign,char,1;
		전일대비,change,change,long,8;
		등락율,diff,diff,float,6.2;
		체결수량,cvolume,cvolume,long,12;
		체결강도,chdegree,chdegree,float,8.2;
		거래량,volume,volume,long,12;
		매도체결수량,mdvolume,mdvolume,long,12;
		매도체결건수,mdchecnt,mdchecnt,long,8;
		매수체결수량,msvolume,msvolume,long,12;
		매수체결건수,mschecnt,mschecnt,long,8;
		순체결량,revolume,revolume,long,12;
		순체결건수,rechecnt,rechecnt,long,8;
	end
	END_DATA_MAP
END_FUNCTION_MAP

