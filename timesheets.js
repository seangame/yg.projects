
function CreateTimebills(data_in) {
	// based on the sample restlet described at
	// http://blog.prolecto.com/2011/12/18/netsuite-restlet-sample-program-exploits-new-power/

	//nlapiLogExecution('DEBUG','createRecord',(typeof data_in.timebill));
	var result = new Object();
	var msg = validateTimeBills(data_in);
	if (msg) {
		result.status = "fail";
		result.message = msg;
		return result;
	}
	var timebills = data_in.timebill;
	for (var timebillobject in timebills) {
		var timebill = timebills[timebillobject];
		var trandate = new Date(timebill.trandate);
		var nsdate = nlapiDateToString(trandate, "date");
		var customer = timebill.customer;
		var casetaskevent = timebill.casetaskevent;
		var hours = timebill.hours;
		var memo = timebill.memo;
		var timebill = nlapiCreateRecord('timebill');
		timebill.setFieldValue('trandate', nsdate);
		timebill.setFieldText('customer', customer);
		timebill.setFieldText('casetaskevent', casetaskevent);
		timebill.setFieldValue('memo', memo);
		timebill.setFieldValue('hours', hours);
		var timebillid = nlapiSubmitRecord(timebill);
		nlapiLogExecution('DEBUG', 'Timebill ' + timebillid + ' successfully created', timebillid);
	}
	result.status = "success";
	result.timebill_id = timebillid;
	return result;
}

function ProjectsFor(data_in) {
	var search_id = 6546;
	return nlapiSearchRecord(null, search_id, null, null);
}

function validateTimeBills(data_in) {
	var timebills = data_in.timebill;
	var returnMessage = "";
	for (var timebillobject in timebills) {
		var timebill = timebills[timebillobject];
		var customer = timebill.customer;
		var casetaskevent = timebill.casetaskevent;
		var hours = timebill.hours;
		var memo = timebill.memo;
		var trandate = new Date(timebill.trandate);
		if (isNaN(trandate)) {
			returnMessage += "Invalid date: '" + timebill.trandate + "' (must be a Javascript Date)\n";
		}
		if (customer == '') {
			returnMessage += "Customer entry cannot be blank.'\n";
		}
		if (hours == '') {
			returnMessage += "Hours cannot be blank.'\n";
		}
	}
	if (returnMessage)
	{
		nlapiLogExecution('DEBUG', 'Validation Error', returnMessage);
		return returnMessage;
	}
}

function GetTimebills(data_in) {
	var filters = new Array();
	if(data_in.date) {
		var js_date = new Date(data_in.date);
		var date = nlapiDateToString(js_date, "date");
		var filter = new nlobjSearchFilter('trandate', null, 'equalTo', date);
		filters.push(filter);
	}
	var results = nlapiSearchRecord('timebill', null, filters);
	return results;
}

function DeleteTimebills(data_in) {
	nlapiDeleteRecord('timebill', data_in.id);
}
