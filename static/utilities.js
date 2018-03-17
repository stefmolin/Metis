function disableScrolling(){
  document.body.style.overflowX = "hidden";
  document.body.style.overflowY = "hidden";
}

function enableScrolling(){
  document.body.style.overflow = "auto";
}

function filterDates(dates){
  var start_date = dates[0];
  var date_break = 14;
  dates.reverse();
  for(i = 0; i < dates.length; i++){
  	if(i % date_break !== 0){
      	dates[i] = "";
    }
  }
  
  if(dates.length < date_break){
    dates[dates.length - 1] = start_date;
  }
  return dates.reverse();
}